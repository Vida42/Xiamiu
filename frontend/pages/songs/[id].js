import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import NextLink from 'next/link';
import { Box, Heading, Text, Image, Flex, Badge, Link, Divider, VStack, Button, useDisclosure } from '@chakra-ui/react';
import { api } from '../../utils/api';
import XiamiuLayout from '../../components/Layout/XiamiuLayout';
import { StarRating, CommentForm, CommentItem, DeleteConfirmationDialog } from '../../components';
import { formatDate } from '../../utils/formatters';
import { useToast } from '@chakra-ui/react';
import { useAuth } from '../../contexts/AuthContext';

// SectionHeader component for consistent styling
const SectionHeader = ({ title }) => {
  return (
    <Flex justify="space-between" align="center" mb={4}>
      <Heading 
        size="md" 
        fontFamily="'Microsoft YaHei', 'STHeiti', sans-serif"
        color="black"
        fontWeight="bold"
      >
        {title}
      </Heading>
    </Flex>
  );
};

export default function SongDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [song, setSong] = useState(null);
  const [songMeta, setSongMeta] = useState(null);
  const [album, setAlbum] = useState(null);
  const [albumMeta, setAlbumMeta] = useState(null);
  const [artist, setArtist] = useState(null);
  const [comments, setComments] = useState([]);
  const [songRating, setSongRating] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const toast = useToast();
  const { isAuthenticated, user } = useAuth();
  const [commentToDelete, setCommentToDelete] = useState(null);
  const { isOpen: isDeleteDialogOpen, onOpen: openDeleteDialog, onClose: closeDeleteDialog } = useDisclosure();

  useEffect(() => {
    const fetchSongData = async () => {
      if (!id) return;
      
      try {
        setIsLoading(true);
        
        // Fetch song details
        const songData = await api.getSong(id);
        setSong(songData);
        
        // Try to fetch song rating
        try {
          const ratingData = await api.getSongRating(id);
          setSongRating(ratingData);
        } catch (ratingErr) {
          console.log('No rating available for this song');
        }
        
        // Try to fetch album details
        try {
          const albumData = await api.getAlbum(songData.album_id);
          setAlbum(albumData);
          
          // Try to fetch album metadata (for cover image)
          try {
            const albumMetaData = await api.getAlbumMeta(albumData.album_id);
            setAlbumMeta(albumMetaData);
          } catch (albumMetaErr) {
            console.log('No album metadata available');
          }
          
          // Try to fetch artist details
          try {
            const artistData = await api.getArtist(albumData.artist_id);
            setArtist(artistData);
          } catch (artistErr) {
            console.log('No artist details available');
          }
        } catch (albumErr) {
          console.log('No album details available');
        }
        
        // Try to fetch song metadata (lyrics)
        try {
          const metaData = await api.getSongMeta(id);
          setSongMeta(metaData);
        } catch (metaErr) {
          console.log('No metadata available for this song');
        }
        
        // Try to fetch song comments
        try {
          const commentsData = await api.getSongComments(id);
          // Enhance comments with user data
          const enhancedComments = await Promise.all(
            commentsData.map(async (comment) => {
              try {
                if (comment.user_id) {
                  const userData = await api.getUser(comment.user_id);
                  return {
                    ...comment,
                    user_name: userData.user_name
                  };
                }
                return comment;
              } catch (error) {
                console.log(`Error fetching user info for comment ${comment.id}:`, error);
                return comment;
              }
            })
          );
          setComments(enhancedComments);
        } catch (commentsErr) {
          console.log('No comments available for this song');
        }
        
      } catch (err) {
        console.error('Error fetching song data:', err);
        setError('Failed to load song details. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSongData();
  }, [id]);

  const handleCommentSubmit = async (comment) => {
    try {
      await api.addSongComment(id, comment);
      // Refresh comments
      const updatedComments = await api.getSongComments(id);
      setComments(updatedComments);
      toast({
        title: "Comment added",
        description: "Your comment has been added successfully.",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Error adding comment:', error);
      toast({
        title: "Error",
        description: "Failed to add the comment. Please try again.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const handleDeleteComment = async () => {
    if (!commentToDelete) return;
    
    try {
      await api.deleteSongComment(commentToDelete.id);
      // Remove the comment from the local state
      setComments(comments.filter(c => c.id !== commentToDelete.id));
      toast({
        title: "Comment deleted",
        description: "Your comment has been deleted successfully.",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Error deleting comment:', error);
      toast({
        title: "Error",
        description: "Failed to delete the comment. Please try again.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    } finally {
      closeDeleteDialog();
      setCommentToDelete(null);
    }
  };

  // Function to render star rating
  const renderStarRating = (rating) => {
    if (!rating) return null;
    const stars = '★'.repeat(rating) + '☆'.repeat(5 - rating);
    return <Text as="span" color="orange.400">{stars}</Text>;
  };

  const renderContent = () => {
    if (!id) return null;

    if (error) {
      return (
        <Box textAlign="center" py={10}>
          <Heading mb={4}>Error</Heading>
          <Text>{error}</Text>
        </Box>
      );
    }

    if (isLoading) {
      return (
        <Box textAlign="center" py={10}>
          <Text>Loading song details...</Text>
        </Box>
      );
    }

    if (!song) {
      return (
        <Box textAlign="center" py={10}>
          <Heading mb={4}>Song Not Found</Heading>
          <Text>The song you're looking for doesn't exist.</Text>
          <NextLink href="/songs" passHref legacyBehavior>
            <Link color="blue.500" mt={4} display="inline-block">
              Back to Songs
            </Link>
          </NextLink>
        </Box>
      );
    }

    return (
      <Box maxW="1200px" mx="auto" px={4} py={8}>
        <Box mb={8}>
          <Flex direction={{ base: 'column', md: 'row' }} gap={8}>
            <Box flexShrink={0} maxW={{ base: '100%', md: '300px' }}>
              <Image
                src={albumMeta?.pic_address || '/album-placeholder.svg'}
                alt={album?.name || song.name}
                borderRadius="lg"
                width="260px"
                height="260px"
                objectFit="cover"
                crossOrigin="anonymous"
                fallbackSrc="/album-placeholder.svg"
              />
              <Flex justify="center" mt={2}>
                <StarRating rating={songRating?.average_rating || 0} size="lg" />
              </Flex>
            </Box>
            
            <Box>
              <Heading size="lg" mb={4}>{song.name}</Heading>
              
              <VStack spacing={2} align="flex-start">
                {album && (
                  <Flex>
                    <Text width="120px">Album:</Text>
                    <NextLink href={`/albums/${album.album_id}`} passHref legacyBehavior>
                      <Link color="blue.500">{album.name}</Link>
                    </NextLink>
                  </Flex>
                )}
                
                {artist && (
                  <Flex>
                    <Text width="120px">Artist:</Text>
                    <NextLink href={`/artists/${artist.artist_id}`} passHref legacyBehavior>
                      <Link color="blue.500">{artist.name}</Link>
                    </NextLink>
                  </Flex>
                )}
                
                <Flex>
                  <Text width="120px">Rating:</Text>
                  <Text>{songRating?.average_rating ? `${songRating.average_rating}` : 'No rating now'}</Text>
                </Flex>
              </VStack>
            </Box>
          </Flex>
        </Box>
        
        {/* Lyrics Section */}
        <Box mt={8}>
          <Heading size="md" mb={4}>Lyrics</Heading>
          <Box bg="gray.50" p={4} borderRadius="md">
            <Text whiteSpace="pre-wrap">{songMeta?.lyrics || 'NO LYRICS FOR NOW'}</Text>
          </Box>
        </Box>
        
        {/* Comments Section */}
        <Box mt={8} mb={8}>
          <SectionHeader title={`Comments (${comments.length})`} />
          
          {isAuthenticated && (
            <Box mb={6} p={4} bg="gray.50" borderRadius="md">
              <CommentForm
                onSubmit={handleCommentSubmit}
                showRating={true}
                maxChars={200}
                placeholder="Share your thoughts about this song (200 characters max)"
              />
            </Box>
          )}
          
          {comments.length === 0 ? (
            <Text py={4}>No comments available for this song.</Text>
          ) : (
            <VStack spacing={4} align="stretch">
              {comments.map(comment => (
                <CommentItem
                  key={comment.id}
                  comment={comment}
                  currentUser={user}
                  onDeleteClick={(comment) => {
                    setCommentToDelete(comment);
                    openDeleteDialog();
                  }}
                  formatDate={(date) => new Date(date).toLocaleDateString('en-US', { 
                    month: 'numeric', 
                    day: 'numeric', 
                    year: 'numeric'
                  })}
                  variant="song"
                />
              ))}
            </VStack>
          )}
          
          <DeleteConfirmationDialog
            isOpen={isDeleteDialogOpen}
            onClose={closeDeleteDialog}
            onDelete={handleDeleteComment}
          />
        </Box>
      </Box>
    );
  };

  return (
    <XiamiuLayout>
      {renderContent()}
    </XiamiuLayout>
  );
} 