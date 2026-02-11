import React from 'react';
import { ACTION_COLORS } from '../utils/constants';

const Legend = ({ visibleActions = [] }) => {
    return (
        <div className="bg-gray-800 p-4 rounded-lg shadow-lg min-w-[200px]">
            <h3 className="text-lg font-bold mb-4 border-b border-gray-700 pb-2">Legend</h3>
            <div className="space-y-3">
                {visibleActions.map((action) => {
                    const colorClass = ACTION_COLORS[action] || ACTION_COLORS['default'];
                    return (
                        <div key={action} className="flex items-center gap-3">
                            <div className={`w-4 h-4 rounded-full ${colorClass} shadow-sm border border-white/20`}></div>
                            <span className="text-sm text-gray-300 font-medium capitalize">{action.replace(/_/g, ' ')}</span>
                        </div>
                    );
                })}
                {visibleActions.length === 0 && (
                    <div className="text-gray-500 text-sm italic">No actions yet...</div>
                )}
            </div>
        </div>
    );
};

export default Legend;
