
export const parseLogFile = (content) => {
    const lines = content.trim().split('\n');
    const logs = lines.map(line => {
        try {
            return JSON.parse(line);
        } catch (e) {
            console.error('Failed to parse line:', line, e);
            return null;
        }
    }).filter(log => log !== null);

    if (logs.length === 0) return { logs: [], gridSize: { width: 0, height: 0 } };

    // Calculate grid size and active nodes
    let maxX = 0;
    let maxY = 0;
    const nodeStats = {};

    logs.forEach(log => {
        if (log.from) {
            maxX = Math.max(maxX, log.from[0]);
            maxY = Math.max(maxY, log.from[1]);
            nodeStats[`${log.from[0]},${log.from[1]}`] = true;
        }
        if (log.to) {
            maxX = Math.max(maxX, log.to[0]);
            maxY = Math.max(maxY, log.to[1]);
            nodeStats[`${log.to[0]},${log.to[1]}`] = true;
        }
    });

    // Group logs by msgid to form routes
    const messageGroups = {};
    logs.forEach(log => {
        const msgid = log.msgid || `single-${log.timestamp}`;
        if (!messageGroups[msgid]) {
            messageGroups[msgid] = [];
        }
        messageGroups[msgid].push(log);
    });

    // Create routes from grouped messages
    const routes = [];
    Object.entries(messageGroups).forEach(([msgid, hops]) => {
        // Sort hops by timestamp
        hops.sort((a, b) => a.timestamp - b.timestamp);

        // Build waypoints from the hop sequence
        const waypoints = [];
        hops.forEach((hop, idx) => {
            if (idx === 0) {
                // First hop: add both from and to
                waypoints.push(hop.from);
            }
            waypoints.push(hop.to);
        });

        // Calculate total distance as sum of segment distances with wraparound
        let totalDistance = 0;
        for (let i = 0; i < waypoints.length - 1; i++) {
            let dx = waypoints[i + 1][0] - waypoints[i][0];
            let dy = waypoints[i + 1][1] - waypoints[i][1];

            // Use shortest path considering wraparound
            if (Math.abs(dx) > (maxX + 1) / 2) {
                dx = dx > 0 ? dx - (maxX + 1) : dx + (maxX + 1);
            }
            if (Math.abs(dy) > (maxY + 1) / 2) {
                dy = dy > 0 ? dy - (maxY + 1) : dy + (maxY + 1);
            }

            totalDistance += Math.sqrt(dx * dx + dy * dy);
        }

        routes.push({
            id: msgid,
            msgid: msgid,
            timestamp: hops[0].timestamp,
            action: hops[0].action,
            waypoints: waypoints,
            distance: totalDistance,
            hops: hops // Keep original hops for reference
        });
    });

    // Normalize timestamps
    const minTime = Math.min(...routes.map(r => r.timestamp));
    const normalizedRoutes = routes.map(route => {
        return {
            ...route,
            normalizedTime: route.timestamp - minTime,
        };
    }).sort((a, b) => a.normalizedTime - b.normalizedTime);

    return {
        logs: normalizedRoutes,
        gridSize: { width: maxX + 1, height: maxY + 1 }, // +1 because 0-indexed
        nodeStats,
        duration: normalizedRoutes[normalizedRoutes.length - 1].normalizedTime
    };
};
