import React from 'react';

/**
 * A reusable Skeleton component for loading states.
 * Use specialized variants for common shapes.
 */
export function Skeleton({ className = '', style = {} }) {
  return <div className={`skeleton ${className}`} style={style} />;
}

export function SkeletonText({ lines = 3, className = '' }) {
  return (
    <div className={`skeleton-container ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton 
          key={i} 
          className="skeleton-text" 
          style={{ width: i === lines - 1 && lines > 1 ? '70%' : '100%' }} 
        />
      ))}
    </div>
  );
}

export function SkeletonTitle({ className = '' }) {
  return <Skeleton className={`skeleton-title ${className}`} />;
}

export function SkeletonRect({ height = 100, className = '' }) {
  return <Skeleton className={`skeleton-rect ${className}`} style={{ height }} />;
}

export function SkeletonCircle({ size = 40, className = '' }) {
  return <Skeleton className={`skeleton-circle ${className}`} style={{ width: size, height: size }} />;
}

export default Skeleton;
