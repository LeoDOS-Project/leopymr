import React from 'react';
import { ACTION_COLORS, ACTION_Border_COLORS } from '../utils/constants';

const GridVisualization = ({ gridSize, activeMessages, nodeStats, nodeColors = {} }) => {
    const { width, height } = gridSize;

    // Create grid cells
    const cells = [];
    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            const isNode = nodeStats[`${x},${y}`]; // Check if this cell is ever used as a node
            const actionName = nodeColors[`${x},${y}`];
            const activeColorClass = actionName ? (ACTION_COLORS[actionName] || ACTION_COLORS['default']) : null;

            cells.push(
                <div
                    key={`${x}-${y}`}
                    className={`w-full aspect-square border border-gray-700 flex items-center justify-center relative transition-colors duration-200
            ${activeColorClass ? activeColorClass : (isNode ? 'bg-gray-800' : 'bg-transparent')}
          `}
                >
                    {isNode && (
                        <div className="text-[10px] sm:text-xs text-gray-500">{x},{y}</div>
                    )}
                </div>
            );
        }
    }

    return (
        <div
            className="relative"
            style={{
                aspectRatio: `${width} / ${height}`,
                height: '100%',
                maxHeight: '100%',
                maxWidth: '100%',
                // We rely on parent flex centering to position this.
                // But if width is constrained, height handles itself via aspect-ratio.
                // If height is constrained, width handles itself via aspect ratio.
                // However, 'height: 100%' might force it to be parent height, ignoring aspect ratio if width allows?
                // Actually, standard object-contain behavior:
                // We want the box to be AS BIG AS POSSIBLE within parent constraints while maintaining Aspect Ratio.
                // CSS doesn't have a single property for this on div (unlike img object-fit).
                // But:
                // If we set maxHeight: 100% and maxWidth: 100% and aspectRatio...
                // And auto width/height?
                // If I say h-full -> it takes full height. Width becomes h * ratio.
                // If h * ratio > max-width ... then what? overflow.

                // Better approach:
                // width: min(100%, 100% * (ratio / parentRatio)) ?? No JS for parent ratio here.

                // Let's rely on the container being flex center.
                // Then:
                marginLeft: 'auto',
                marginRight: 'auto',

                // This trick often works:
                // display: 'grid'
            }}
        >
            <div
                className="grid gap-0.5 w-full h-full"
                style={{
                    gridTemplateColumns: `repeat(${width}, 1fr)`,
                    gridTemplateRows: `repeat(${height}, 1fr)` // Also force rows to distribute height
                }}
            >
                {cells}

                {/* SVG Overlay for Lines */}
                <svg className="absolute top-0 left-0 w-full h-full pointer-events-none overflow-visible">
                    {activeMessages.map((msg, idx) => {
                        const strokeColor = msg.action === 'collect' ? '#3b82f6' :
                            msg.action === 'collect_data' ? '#22c55e' :
                                msg.action === 'set_map_count' ? '#eab308' :
                                    msg.action === 'reduce_data' ? '#a855f7' : '#6b7280';

                        // Coordinates: % based
                        // Center of cell x = (x + 0.5) / width * 100 %
                        const x1 = `${(msg.from[0] + 0.5) / width * 100}%`;
                        const y1 = `${(msg.from[1] + 0.5) / height * 100}%`;
                        const x2 = `${(msg.to[0] + 0.5) / width * 100}%`;
                        const y2 = `${(msg.to[1] + 0.5) / height * 100}%`;

                        return (
                            <line
                                key={`line-${idx}`}
                                x1={x1}
                                y1={y1}
                                x2={x2}
                                y2={y2}
                                stroke={strokeColor}
                                strokeWidth="2"
                                vectorEffect="non-scaling-stroke"
                                strokeDasharray="4"
                                opacity="0.5"
                            />
                        );
                    })}
                </svg>

                {/* Moving Dots */}
                {activeMessages.map((msg, idx) => {
                    const colorClass = ACTION_COLORS[msg.action] || ACTION_COLORS['default'];
                    return (
                        <div
                            key={`dot-${idx}`}
                            className={`absolute w-3 h-3 md:w-4 md:h-4 rounded-full ${colorClass} shadow-lg z-10 pointer-events-none transition-transform will-change-transform border border-white`}
                            style={{
                                left: `${(msg.x + 0.5) / width * 100}%`,
                                top: `${(msg.y + 0.5) / height * 100}%`,
                                transform: `translate(-50%, -50%)`, // Center the dot on the coordinate
                            }}
                            title={msg.action}
                        />
                    )
                })}
            </div>
        </div>
    );
};

export default GridVisualization;
