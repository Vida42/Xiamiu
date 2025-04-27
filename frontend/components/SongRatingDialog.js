import { useState, useEffect } from 'react';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Button,
  Textarea,
  FormControl,
  FormLabel,
  Text,
  Box,
  Flex,
  Alert,
  AlertIcon,
  HStack
} from '@chakra-ui/react';
import { FaStar } from 'react-icons/fa';

const SongRatingDialog = ({ 
  isOpen, 
  onClose, 
  songName, 
  initialRating = 0, 
  onSubmit 
}) => {
  const [rating, setRating] = useState(initialRating);
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const maxChars = 100;
  
  // Reset state when dialog opens
  useEffect(() => {
    if (isOpen) {
      setRating(initialRating);
      setComment('');
      setError('');
    }
  }, [isOpen, initialRating]);
  
  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError('');
    
    try {
      // Send the rating directly (1-5 scale)
      await onSubmit(rating, comment);
    } catch (error) {
      console.error('Error submitting song rating:', error);
      setError(error.message || 'Failed to submit rating. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return (
    <Modal isOpen={isOpen} onClose={onClose} isCentered>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Rate "{songName}"</ModalHeader>
        <ModalCloseButton />
        
        <ModalBody>
          {error && (
            <Alert status="error" mb={4} borderRadius="md">
              <AlertIcon />
              {error}
            </Alert>
          )}
          
          <FormControl mb={4}>
            <FormLabel>Your Rating</FormLabel>
            <Flex justify="center" mb={2}>
              <HStack spacing={2}>
                {[1, 2, 3, 4, 5].map((starValue) => (
                  <Box 
                    key={starValue}
                    as="button"
                    onClick={() => setRating(starValue)}
                    color={starValue <= rating ? "yellow.400" : "gray.300"}
                    fontSize="28px"
                    lineHeight="1"
                    cursor="pointer"
                    transitionDuration="200ms"
                    _hover={{ transform: "scale(1.15)" }}
                  >
                    <FaStar />
                  </Box>
                ))}
              </HStack>
            </Flex>
            <Text textAlign="center" fontWeight="medium">
              {rating} {rating === 1 ? 'Star' : 'Stars'}
            </Text>
          </FormControl>
          
          <FormControl>
            <FormLabel>Your Comment (Optional)</FormLabel>
            <Box position="relative">
              <Textarea
                value={comment}
                onChange={(e) => {
                  if (e.target.value.length <= maxChars) {
                    setComment(e.target.value);
                  }
                }}
                placeholder="Write your thoughts about this song..."
                rows={4}
                resize="vertical"
              />
              <Text 
                position="absolute" 
                right="8px" 
                bottom="8px"
                fontSize="xs" 
                color={comment.length > maxChars * 0.8 ? "orange.500" : "gray.500"}
              >
                {comment.length}/{maxChars}
              </Text>
            </Box>
          </FormControl>
        </ModalBody>

        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            Cancel
          </Button>
          <Button 
            colorScheme="orange"
            onClick={handleSubmit}
            isLoading={isSubmitting}
            loadingText="Saving..."
          >
            Save
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default SongRatingDialog; 