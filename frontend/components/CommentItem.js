import { Box, Text, Flex, Image, Button, HStack } from '@chakra-ui/react';

const CommentItem = ({ 
  comment, 
  currentUser, 
  onDeleteClick, 
  formatDate = (date) => new Date(date).toLocaleDateString(),
  variant = "album" // Can be "album", "song", or "artist"
}) => {
  // Function to render star rating for song comments
  const renderStarRating = (rating) => {
    if (!rating) return null;
    const stars = '★'.repeat(rating) + '☆'.repeat(5 - rating);
    return <Text as="span" color="orange.400">{stars}</Text>;
  };

  return (
    <Box 
      p={4}
      borderWidth="1px"
      borderRadius="md"
      bg="white"
    >
      <Flex gap={3}>
        <Image
          src="/album-placeholder.svg"
          alt="User avatar"
          boxSize="40px"
          borderRadius="full"
          objectFit="cover"
        />
        <Box flex="1">
          <Flex justify="space-between" align="center" mb={1}>
            <Flex align="baseline">
              <Text fontWeight="bold" mr={1}>
                {comment.user_name || (comment.user_id && `User #${comment.user_id}`) || 'Anonymous User'}:
              </Text>
              <Text>{comment.comment}</Text>
            </Flex>
            {/* Display rating based on variant */}
            {comment.star && variant === "album" && (
              <Text fontSize="sm" color="orange.500" fontWeight="semibold">
                {comment.star}
              </Text>
            )}
            {comment.star && variant === "song" && (
              <Box fontSize="sm" color="orange.500">
                {renderStarRating(comment.star)}
              </Box>
            )}
            {/* For artist variant, no rating is displayed */}
          </Flex>
          <Flex justify="space-between" fontSize="sm" color="gray.500" mt={2}>
            <Text>{formatDate(comment.created)}</Text>
            <Flex align="center" gap={2}>
              <Text>{comment.num_like} likes</Text>
              {currentUser && comment.user_id === currentUser.id && (
                <Button
                  size="xs"
                  colorScheme="red"
                  variant="ghost"
                  onClick={() => onDeleteClick(comment)}
                  height="20px"
                  minWidth="auto"
                  px={2}
                  alignItems="center"
                  lineHeight="1"
                  py={0}
                >
                  Delete
                </Button>
              )}
            </Flex>
          </Flex>
        </Box>
      </Flex>
    </Box>
  );
};

export default CommentItem; 