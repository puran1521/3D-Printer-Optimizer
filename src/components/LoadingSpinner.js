import React from 'react';
import PropTypes from 'prop-types';

const LoadingSpinner = ({ text = 'Loading...', size = 'medium', color = 'primary' }) => {
  const spinnerSizes = { small: '20px', medium: '40px', large: '60px' };
  const spinnerColors = { primary: '#2196f3', secondary: '#f50057', white: '#ffffff', default: '#cccccc' };

  return (
    <div className="loading-container" role="alert" aria-busy="true" aria-live="polite">
      <div 
        className={`loading-spinner spinner-${size} spinner-${color}`}
        title="Loading, please wait..."
        style={{ width: spinnerSizes[size], height: spinnerSizes[size], backgroundColor: spinnerColors[color] || spinnerColors.default }}
      />
      <p className="loading-text">{text}</p>
    </div>
  );
};

LoadingSpinner.propTypes = {
  text: PropTypes.string,
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  color: PropTypes.oneOf(['primary', 'secondary', 'white'])
};

export default LoadingSpinner;