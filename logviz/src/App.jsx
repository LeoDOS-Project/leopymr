import { useState, useCallback, useEffect, useRef, useMemo } from 'react'
import FileUpload from './components/FileUpload'
import GridVisualization from './components/GridVisualization'
import Legend from './components/Legend'
import { parseLogFile } from './utils/logParser'

function App() {
  const [logs, setLogs] = useState([]);
  const [gridSize, setGridSize] = useState({ width: 0, height: 0 });
  const [nodeStats, setNodeStats] = useState({});
  const [duration, setDuration] = useState(0);

  // Animation State
  const [currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(0.005); // 0.005x speed default

  const lastFrameTimeRef = useRef(0);
  const requestRef = useRef();

  const handleFileUpload = useCallback((content) => {
    const { logs, gridSize, nodeStats, duration } = parseLogFile(content);
    setLogs(logs);
    setGridSize(gridSize);
    setNodeStats(nodeStats);
    setDuration(duration);
    setCurrentTime(0);
    setIsPlaying(false);
  }, []);

  // Calculate first appearance time for each action
  const actionFirstTimes = useMemo(() => {
    const times = {};
    logs.forEach(log => {
      if (!log.action) return;
      if (times[log.action] === undefined || log.normalizedTime < times[log.action]) {
        times[log.action] = log.normalizedTime;
      }
    });
    return times;
  }, [logs]);

  // Derive visible actions (excluding 'default')
  const visibleActions = useMemo(() => {
    return Object.keys(actionFirstTimes)
      .filter(action => action !== 'default' && actionFirstTimes[action] <= currentTime)
      .sort((a, b) => actionFirstTimes[a] - actionFirstTimes[b]); // Sort by appearance time
  }, [actionFirstTimes, currentTime]);

  // Dynamic Animation Constants - MUST come before animationDuration
  const { messageSpeed, playbackSpeedInit } = useMemo(() => {
    if (logs.length === 0) return { messageSpeed: 5, playbackSpeedInit: 0.005 };

    const totalDuration = duration > 0 ? duration : 1;

    // Find the worst-case message: the one that requires the highest speed to complete
    // For each message, calculate: requiredSpeed = distance / (duration - startTime)
    let maxRequiredSpeed = 0;
    let totalDist = 0;

    logs.forEach(l => {
      totalDist += l.distance;
      const availableTime = totalDuration - l.normalizedTime;
      if (availableTime > 0 && l.distance > 0) {
        const requiredSpeed = l.distance / availableTime;
        if (requiredSpeed > maxRequiredSpeed) {
          maxRequiredSpeed = requiredSpeed;
        }
      }
    });

    // For visual appeal, we might want messages to take at least some minimum time
    // Let's target 10-15% of simulation duration for typical messages
    const avgDist = totalDist / logs.length;
    const targetMsgDuration = totalDuration * 0.15;
    const visualSpeed = avgDist / targetMsgDuration;

    // Use the faster of the two speeds (to ensure completion while maintaining visual appeal)
    const calcSpeed = Math.max(maxRequiredSpeed, visualSpeed);

    // Auto-adjust playback speed
    // Target total real playback time = ~20 seconds
    const targetRealTime = 20;
    const calcPlayback = totalDuration / targetRealTime;

    return {
      messageSpeed: calcSpeed,
      playbackSpeedInit: calcPlayback
    };
  }, [logs, duration]);

  // Update playback speed on fresh load
  useEffect(() => {
    if (duration > 0) {
      setPlaybackSpeed(playbackSpeedInit);
    }
  }, [playbackSpeedInit, duration]);

  // Scale node action duration proportionally to simulation length
  // For short sims (0.2s), we want a brief flash (0.04s)
  // For long sims (24s), we can afford a longer effect (4.8s, but cap it)
  const dynamicNodeActionDuration = Math.min(1.0, duration * 0.2);

  // Animation duration should match the log duration exactly
  // Messages travel within this timeframe based on messageSpeed
  const animationDuration = duration;

  const animate = useCallback((time) => {
    if (lastFrameTimeRef.current !== undefined) {
      const deltaTime = (time - lastFrameTimeRef.current) / 1000;

      setCurrentTime(prevTime => {
        const newTime = prevTime + deltaTime * playbackSpeed;
        if (newTime >= animationDuration) {
          setIsPlaying(false);
          return animationDuration; // Clamp to end
        }
        return newTime;
      });
    }
    lastFrameTimeRef.current = time;
    if (isPlaying) {
      requestRef.current = requestAnimationFrame(animate);
    }
  }, [animationDuration, isPlaying, playbackSpeed]);

  useEffect(() => {
    if (isPlaying) {
      lastFrameTimeRef.current = performance.now();
      requestRef.current = requestAnimationFrame(animate);
    } else {
      cancelAnimationFrame(requestRef.current);
    }
    return () => cancelAnimationFrame(requestRef.current);
  }, [isPlaying, animate]);


  /*
   * Active Messages: Represents MOVING dots following multi-hop routes.
   */
  const activeMessages = useMemo(() => logs.filter(route => {
    // Start time
    const startTime = route.normalizedTime;
    // Duration = distance / speed
    const msgDuration = route.distance / messageSpeed;
    const endTime = startTime + msgDuration;

    return currentTime >= startTime && currentTime <= endTime;
  }).map(route => {
    const startTime = route.normalizedTime;
    const msgDuration = route.distance / messageSpeed;

    // Avoid division by zero
    const overallProgress = msgDuration > 0 ? (currentTime - startTime) / msgDuration : 1;

    // Calculate position along the multi-segment path
    const waypoints = route.waypoints;
    if (!waypoints || waypoints.length < 2) {
      // Fallback for routes without waypoints
      return { ...route, x: waypoints[0][0], y: waypoints[0][1] };
    }

    // Calculate segment lengths
    const segmentLengths = [];
    let totalLength = 0;
    for (let i = 0; i < waypoints.length - 1; i++) {
      const dx = waypoints[i + 1][0] - waypoints[i][0];
      const dy = waypoints[i + 1][1] - waypoints[i][1];
      const length = Math.sqrt(dx * dx + dy * dy);
      segmentLengths.push(length);
      totalLength += length;
    }

    // Find which segment we're on based on overall progress
    const targetDistance = overallProgress * totalLength;
    let accumulatedDistance = 0;
    let currentSegment = 0;
    let segmentProgress = 0;

    for (let i = 0; i < segmentLengths.length; i++) {
      if (accumulatedDistance + segmentLengths[i] >= targetDistance) {
        currentSegment = i;
        const distanceIntoSegment = targetDistance - accumulatedDistance;
        segmentProgress = segmentLengths[i] > 0 ? distanceIntoSegment / segmentLengths[i] : 0;
        break;
      }
      accumulatedDistance += segmentLengths[i];
    }

    // If we've gone past all segments, clamp to the last waypoint
    if (currentSegment >= waypoints.length - 1) {
      currentSegment = waypoints.length - 2;
      segmentProgress = 1;
    }

    // Interpolate position within the current segment with wraparound
    const from = waypoints[currentSegment];
    const to = waypoints[currentSegment + 1];

    // Calculate shortest path considering wraparound (toroidal topology)
    const dx = to[0] - from[0];
    const dy = to[1] - from[1];

    // Determine if wrapping is shorter
    let wrapX = dx;
    let wrapY = dy;

    if (Math.abs(dx) > gridSize.width / 2) {
      // Wrapping around x-axis is shorter
      wrapX = dx > 0 ? dx - gridSize.width : dx + gridSize.width;
    }

    if (Math.abs(dy) > gridSize.height / 2) {
      // Wrapping around y-axis is shorter
      wrapY = dy > 0 ? dy - gridSize.height : dy + gridSize.height;
    }

    // Interpolate with wraparound, then apply modulo to wrap coordinates
    let x = from[0] + wrapX * segmentProgress;
    let y = from[1] + wrapY * segmentProgress;

    // Apply modulo to handle wraparound visualization
    x = ((x % gridSize.width) + gridSize.width) % gridSize.width;
    y = ((y % gridSize.height) + gridSize.height) % gridSize.height;

    return { ...route, x, y };
  }), [logs, currentTime, messageSpeed, gridSize]);

  // Derive active node colors based on ARRIVAL time
  // Once a message arrives at a node, the color persists (doesn't fade out)
  const nodeColors = useMemo(() => {
    const colors = {};
    logs.forEach(route => {
      const startTime = route.normalizedTime;
      const travelDuration = route.distance / messageSpeed;
      const arrivalTime = startTime + travelDuration;

      // Color the node once the message has arrived (and keep it colored)
      if (currentTime >= arrivalTime && route.waypoints && route.waypoints.length > 0) {
        // Use the final waypoint as the destination
        const destination = route.waypoints[route.waypoints.length - 1];
        const key = `${destination[0]},${destination[1]}`;
        // Later actions override earlier ones if they overlap on the same node
        colors[key] = route.action;
      }
    });
    return colors;
  }, [logs, currentTime, messageSpeed]);

  return (
    <div className="h-screen w-full bg-gray-900 text-white flex flex-col p-4 overflow-hidden">
      <h1 className="text-2xl font-bold mb-4 text-center shrink-0">SpaceCoMP Visualization</h1>

      {logs.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center">
          <div className="w-full max-w-xl">
            <FileUpload onFileUpload={handleFileUpload} />
            <p className="mt-4 text-gray-400 text-center">Upload a JSONL log file to visualize network communication.</p>
          </div>
        </div>
      ) : (
        <div className="flex w-full h-full min-h-0 gap-4">
          {/* Left Sidebar */}
          <div className="shrink-0 flex flex-col gap-4">
            <Legend visibleActions={visibleActions} />
          </div>

          {/* Main Content */}
          <div className="flex flex-col items-center w-full h-full min-h-0 flex-1">
            <div className="shrink-0 flex flex-col items-center w-full bg-gray-900 z-10 pb-4">
              <div className="mb-2 text-lg flex gap-4 items-center">
                <span>Time: {currentTime.toFixed(2)}s / {animationDuration.toFixed(2)}s</span>
                <span>Active Msgs: {activeMessages.length}</span>
              </div>

              <div className="flex gap-4 mb-2 flex-wrap justify-center">
                <button
                  onClick={() => {
                    if (currentTime >= animationDuration) setCurrentTime(0);
                    setIsPlaying(!isPlaying);
                  }}
                  className={`px-3 py-1 rounded font-bold ${isPlaying ? 'bg-yellow-600 hover:bg-yellow-700' : 'bg-green-600 hover:bg-green-700'}`}
                >
                  {isPlaying ? 'Pause' : (currentTime >= animationDuration ? 'Replay' : 'Play')}
                </button>
                <button
                  onClick={() => {
                    setIsPlaying(false);
                    setCurrentTime(0);
                  }}
                  className="px-3 py-1 bg-gray-600 rounded hover:bg-gray-700"
                >
                  Reset
                </button>
                <div className="flex items-center gap-2">
                  <label>Speed:</label>
                  <input
                    type="range"
                    min="0.0001"
                    max={playbackSpeedInit * 5} // Allow going up to 5x default
                    step={playbackSpeedInit / 10}
                    value={playbackSpeed}
                    onChange={(e) => setPlaybackSpeed(parseFloat(e.target.value))}
                    className="w-24"
                  />
                  <span>{playbackSpeed.toFixed(4)}x</span>
                </div>
                <button
                  onClick={() => setLogs([])}
                  className="px-3 py-1 bg-red-600 rounded hover:bg-red-700 transition"
                >
                  Clear Data
                </button>
              </div>

              <div className="mb-2 w-full max-w-2xl">
                <input
                  type="range"
                  min="0"
                  max={animationDuration}
                  step="0.01"
                  value={currentTime}
                  onChange={(e) => {
                    setIsPlaying(false);
                    setCurrentTime(parseFloat(e.target.value));
                  }}
                  className="w-full cursor-pointer"
                />
              </div>
            </div>

            <div className="flex-1 w-full min-h-0 flex items-center justify-center overflow-hidden">
              <GridVisualization
                gridSize={gridSize}
                activeMessages={activeMessages}
                nodeStats={nodeStats}
                nodeColors={nodeColors}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App

