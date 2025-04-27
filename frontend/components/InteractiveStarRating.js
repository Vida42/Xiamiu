import { useState, useEffect } from 'react';
import { Box, Flex, Icon } from '@chakra-ui/react';
import { FaStar } from 'react-icons/fa';

const InteractiveStarRating = ({
  initialRating = 0,
  maxStars = 5,
  size = 'md',
  spacing = 1,
  onRatingChange,
  onRatingSelect,
  resetOnClick = false
}) => {
  const [hoverRating, setHoverRating] = useState(0);
  const [selectedRating, setSelectedRating] = useState(initialRating);
  
  // Update the selected rating when initialRating changes
  useEffect(() => {
    setSelectedRating(initialRating);
    setHoverRating(0);
  }, [initialRating]);
  
  // Define star sizes based on the size prop
  const starSizes = {
    xs: "14px",
    sm: "16px",
    md: "18px",
    lg: "22px",
    xl: "26px",
  };

  // Define colors
  const activeColor = "#FFD700"; // Gold/yellow for active stars
  const inactiveColor = "#333333"; // Dark color for inactive stars

  const handleMouseEnter = (index) => {
    const newRating = index + 1;
    setHoverRating(newRating);
    if (onRatingChange) {
      onRatingChange(newRating);
    }
  };

  const handleMouseLeave = () => {
    setHoverRating(0);
    if (onRatingChange) {
      onRatingChange(selectedRating);
    }
  };

  const handleClick = (index) => {
    const newRating = index + 1;
    if (resetOnClick) {
      // Reset both hover and selected ratings immediately
      setHoverRating(0);
      setSelectedRating(initialRating);
    }
    if (onRatingSelect) {
      onRatingSelect(newRating);
    }
  };

  // Determine which rating to display (hover rating takes precedence)
  const displayRating = hoverRating > 0 ? hoverRating : selectedRating;

  return (
    <Flex align="center" gap={spacing}>
      {[...Array(maxStars)].map((_, index) => (
        <Icon
          key={`star-${index}`}
          as={FaStar}
          color={index < displayRating ? activeColor : inactiveColor}
          w={starSizes[size]}
          h={starSizes[size]}
          cursor="pointer"
          onMouseEnter={() => handleMouseEnter(index)}
          onMouseLeave={handleMouseLeave}
          onClick={() => handleClick(index)}
        />
      ))}
    </Flex>
  );
};

export default InteractiveStarRating; 