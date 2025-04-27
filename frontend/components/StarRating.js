import { Box, Flex, Icon } from "@chakra-ui/react";
import { FaStar } from "react-icons/fa";
import { useState } from "react";

const StarRating = ({ 
  rating = 0, 
  maxStars = 5, 
  size = "md", 
  spacing = 1,
  isInteractive = false,
  onChange = null
}) => {
  const [hoverRating, setHoverRating] = useState(0);
  
  // Ensure rating is a valid number and within range
  const validRating = !isNaN(parseFloat(rating)) ? 
    Math.max(0, Math.min(parseFloat(rating), maxStars)) : 0;
  
  // Calculate the whole stars and the decimal part
  const fullStars = Math.floor(validRating);
  const decimalPart = validRating % 1;
  
  // Define star sizes based on the size prop
  const starSizes = {
    xs: "12px",
    sm: "14px",
    md: "16px",
    lg: "20px",
    xl: "24px",
  };

  // Define colors
  const activeColor = "#FFD700"; // Gold/yellow for active stars
  const inactiveColor = "#333333"; // Dark color for inactive stars (to match pic 3)

  // Event handlers for interactive mode
  const handleMouseEnter = (index) => {
    if (isInteractive) {
      setHoverRating(index + 1);
    }
  };

  const handleMouseLeave = () => {
    if (isInteractive) {
      setHoverRating(0);
    }
  };

  const handleClick = (index) => {
    if (isInteractive && onChange) {
      onChange(index + 1);
    }
  };

  // Determine which rating to display (hover rating takes precedence in interactive mode)
  const displayRating = hoverRating > 0 ? hoverRating : validRating;
  const displayFullStars = Math.floor(displayRating);
  const displayDecimalPart = displayRating % 1;

  // Render a single star with appropriate styling
  const renderStar = (index) => {
    // If index is less than the full number of stars, render a full gold star
    if (index < displayFullStars) {
      return (
        <Icon 
          key={`star-${index}`} 
          as={FaStar} 
          color={activeColor} 
          w={starSizes[size]} 
          h={starSizes[size]} 
          cursor={isInteractive ? "pointer" : "default"}
          onMouseEnter={() => handleMouseEnter(index)}
          onMouseLeave={handleMouseLeave}
          onClick={() => handleClick(index)}
        />
      );
    }
    
    // If this is where the half star should be
    if (index === displayFullStars && displayDecimalPart >= 0.5) {
      return (
        <Box 
          key={`star-${index}`} 
          position="relative" 
          w={starSizes[size]} 
          h={starSizes[size]}
          cursor={isInteractive ? "pointer" : "default"}
          onMouseEnter={() => handleMouseEnter(index)}
          onMouseLeave={handleMouseLeave}
          onClick={() => handleClick(index)}
        >
          {/* Background dark star */}
          <Icon 
            as={FaStar} 
            color={inactiveColor} 
            w={starSizes[size]} 
            h={starSizes[size]} 
            position="absolute"
          />
          {/* Foreground half gold star */}
          <Box position="absolute" width="50%" height="100%" overflow="hidden">
            <Icon 
              as={FaStar} 
              color={activeColor} 
              w={starSizes[size]} 
              h={starSizes[size]} 
            />
          </Box>
        </Box>
      );
    }
    
    // Otherwise render an empty (dark) star
    return (
      <Icon 
        key={`star-${index}`} 
        as={FaStar} 
        color={inactiveColor} 
        w={starSizes[size]} 
        h={starSizes[size]} 
        cursor={isInteractive ? "pointer" : "default"}
        onMouseEnter={() => handleMouseEnter(index)}
        onMouseLeave={handleMouseLeave}
        onClick={() => handleClick(index)}
      />
    );
  };

  return (
    <Flex 
      align="center" 
      gap={spacing}
    >
      {[...Array(maxStars)].map((_, index) => renderStar(index))}
    </Flex>
  );
};

export default StarRating; 