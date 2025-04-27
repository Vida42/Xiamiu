import { useState } from 'react';
import { 
  Box, 
  Button, 
  Textarea, 
  FormControl, 
  FormErrorMessage, 
  Text, 
  Flex, 
  InputGroup, 
  InputRightElement,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Grid,
  GridItem,
  VStack
} from '@chakra-ui/react';
import { StarRating } from '.';

const CommentForm = ({ 
  onSubmit, 
  showRating = false, 
  maxChars = 200,
  placeholder = "Write your comment..."
}) => {
  const [comment, setComment] = useState('');
  const [rating, setRating] = useState(50); // Default to middle of 1-100 range
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const handleCommentChange = (e) => {
    const value = e.target.value;
    if (value.length <= maxChars) {
      setComment(value);
      setError('');
    }
  };

  const handleRatingChange = (value) => {
    // Ensure the value is within 1-100 range
    const newRating = Math.min(100, Math.max(1, value));
    setRating(newRating);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate the form
    if (!comment.trim()) {
      setError('Comment cannot be empty');
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      // For non-rating comments (like artist comments), we don't send the rating
      await onSubmit(comment, showRating ? rating : null);
      
      // Reset form on success
      setComment('');
      setRating(50);
      setError('');
    } catch (err) {
      // Display the specific error message from the API if available
      setError(err.message || 'Failed to submit your comment. Please try again.');
      console.error('Comment submission error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  // Function to render a custom rating selector (1-100)
  const renderRatingSelector = () => {
    return (
      <VStack spacing={4} align="stretch" h="100%">
        <Text fontSize="sm" fontWeight="medium">Your rating (1-100):</Text>
        <Box flex="1">
          <input
            type="range"
            min="1"
            max="100"
            value={rating}
            onChange={(e) => handleRatingChange(parseInt(e.target.value))}
            style={{ width: '100%', height: '24px' }}
          />
        </Box>
        <NumberInput
          min={1}
          max={100}
          value={rating}
          onChange={(valueString) => handleRatingChange(parseInt(valueString))}
          size="sm"
        >
          <NumberInputField />
          <NumberInputStepper>
            <NumberIncrementStepper />
            <NumberDecrementStepper />
          </NumberInputStepper>
        </NumberInput>
      </VStack>
    );
  };

  return (
    <Box as="form" onSubmit={handleSubmit} width="100%">
      <Grid templateColumns={showRating ? "2fr 1fr" : "1fr"} gap={4} alignItems="stretch">
        <GridItem>
          <FormControl isInvalid={!!error} h="100%">
            <InputGroup h="100%">
              <Textarea
                value={comment}
                onChange={handleCommentChange}
                placeholder={placeholder}
                rows={4}
                resize="vertical"
                h="100%"
                minH="150px"
              />
              <InputRightElement right="8px" bottom="8px" height="auto">
                <Text fontSize="xs" color={comment.length > maxChars * 0.8 ? "orange.500" : "gray.500"}>
                  {comment.length}/{maxChars}
                </Text>
              </InputRightElement>
            </InputGroup>
            {error && <FormErrorMessage>{error}</FormErrorMessage>}
          </FormControl>
        </GridItem>
        
        {showRating && (
          <GridItem>
            {renderRatingSelector()}
          </GridItem>
        )}
      </Grid>
      
      <Button
        mt={3}
        colorScheme="orange"
        type="submit"
        isLoading={isSubmitting}
        loadingText="Submitting..."
      >
        Submit
      </Button>
    </Box>
  );
};

export default CommentForm; 