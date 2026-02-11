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

  const animate = useCallback((time) => {
    if (lastFrameTimeRef.current !== undefined) {
      const deltaTime = (time - lastFrameTimeRef.current) / 1000;

      setCurrentTime(prevTime => {
        const newTime = prevTime + deltaTime * playbackSpeed;
        if (newTime >= duration + 2) { // Add some buffer at end
          setIsPlaying(false);
          return prevTime; // Stop at end? or loop? Stop for now.
        }
        return newTime;
      });
    }
    lastFrameTimeRef.current = time;
    if (isPlaying) {
      requestRef.current = requestAnimationFrame(animate);
    }
  }, [duration, isPlaying, playbackSpeed]);

  useEffect(() => {
    if (isPlaying) {
      lastFrameTimeRef.current = performance.now();
      requestRef.current = requestAnimationFrame(animate);
    } else {
      cancelAnimationFrame(requestRef.current);
    }
    return () => cancelAnimationFrame(requestRef.current);
  }, [isPlaying, animate]);

  // Derive active messages for current time
  // A message is active if it started before currentTime and hasn't finished.
  // We need to define duration of a message.
  // Assumption: Message speed is constant? Or fixed duration?
  // Let's say speed = 5 grid units per second (variable).
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

  const MESSAGE_SPEED = 5;
  const NODE_ACTION_DURATION = 1.0; // Duration for messages that stay on the same node

  /* 
   * Active Messages: Represents MOVING dots.
   * If distance is 0, duration is 0, so it won't be active as a moving message.
   * This is correct because the user wants "cell coloring" for effects, not a stationary dot.
   */
  const activeMessages = useMemo(() => logs.filter(log => {
    // Start time
    const startTime = log.normalizedTime;
    // Duration = distance / speed
    const msgDuration = log.distance / MESSAGE_SPEED;
    const endTime = startTime + msgDuration;

    return currentTime >= startTime && currentTime <= endTime;
  }).map(log => {
    const startTime = log.normalizedTime;
    const msgDuration = log.distance / MESSAGE_SPEED;

    // Avoid division by zero
    const progress = msgDuration > 0 ? (currentTime - startTime) / msgDuration : 1;

    // Lerp position (handles from==to naturally, x=from[0])
    const x = log.from[0] + (log.to[0] - log.from[0]) * progress;
    const y = log.from[1] + (log.to[1] - log.from[1]) * progress;

    return { ...log, x, y };
  }), [logs, currentTime]);

  // Derive active node colors based on ARRIVAL time
  const nodeColors = useMemo(() => {
    const colors = {};
    // We check all logs to see if they are in their "active effect" window on the destination node
    // Effect window: [Arrival Time, Arrival Time + NODE_ACTION_DURATION]
    logs.forEach(log => {
      const startTime = log.normalizedTime;
      const travelDuration = log.distance / MESSAGE_SPEED;
      const arrivalTime = startTime + travelDuration;
      const effectEndTime = arrivalTime + NODE_ACTION_DURATION;

      if (currentTime >= arrivalTime && currentTime < effectEndTime) {
        const key = `${log.to[0]},${log.to[1]}`;
        // Later actions override earlier ones if they overlap on the same node
        colors[key] = log.action;
      }
    });
    return colors;
  }, [logs, currentTime]);

  return (
    <div className="h-screen w-full bg-gray-900 text-white flex flex-col p-4 overflow-hidden">
      <h1 className="text-2xl font-bold mb-4 text-center shrink-0">CoMP Visualization</h1>

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
                <span>Time: {currentTime.toFixed(2)}s / {duration.toFixed(2)}s</span>
                <span>Active Msgs: {activeMessages.length}</span>
              </div>

              <div className="flex gap-4 mb-2 flex-wrap justify-center">
                <button
                  onClick={() => setIsPlaying(!isPlaying)}
                  className={`px-3 py-1 rounded font-bold ${isPlaying ? 'bg-yellow-600 hover:bg-yellow-700' : 'bg-green-600 hover:bg-green-700'}`}
                >
                  {isPlaying ? 'Pause' : 'Play'}
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
                    min="0.001"
                    max="1"
                    step="0.001"
                    value={playbackSpeed}
                    onChange={(e) => setPlaybackSpeed(parseFloat(e.target.value))}
                    className="w-24"
                  />
                  <span>{playbackSpeed}x</span>
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
                  max={duration + 0.1}
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

