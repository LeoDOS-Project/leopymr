
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

    // Normalize timestamps
    const minTime = Math.min(...logs.map(l => l.timestamp));
    const normalizedLogs = logs.map(log => {
        // Calculate distance
        const dx = log.to[0] - log.from[0];
        const dy = log.to[1] - log.from[1];
        const distance = Math.sqrt(dx * dx + dy * dy);

        return {
            ...log,
            normalizedTime: log.timestamp - minTime,
            distance,
        };
    }).sort((a, b) => a.normalizedTime - b.normalizedTime);

    return {
        logs: normalizedLogs,
        gridSize: { width: maxX + 1, height: maxY + 1 }, // +1 because 0-indexed
        nodeStats,
        duration: normalizedLogs[normalizedLogs.length - 1].normalizedTime
    };
};
