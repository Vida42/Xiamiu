import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/router';
import NextLink from 'next/link';
import { Box, Heading, Text, Image, Flex, Badge, Link, Divider, Table, Thead, Tbody, Tr, Td, Th, VStack, useDisclosure, useToast, Button } from '@chakra-ui/react';
import { api } from '../../utils/api';
import XiamiuLayout from '../../components/Layout/XiamiuLayout';
import { StarRating, CommentForm, SongRatingDialog, InteractiveStarRating, CommentItem, DeleteConfirmationDialog } from '../../components';
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

// Function to render star rating with half-stars support
const renderStars = (rating) => {
  if (!rating) return null;
  
  const fullStars = Math.floor(rating);
  const hasHalfStar = rating % 1 >= 0.5;
  
  return (
    <Flex align="center">
      {[...Array(fullStars)].map((_, i) => (
        <Text key={i} fontSize="xl" lineHeight="1">⭐</Text>
      ))}
      {hasHalfStar && <Text fontSize="xl" lineHeight="1">★</Text>}
    </Flex>
  );
};

export default function AlbumDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [album, setAlbum] = useState(null);
  const [albumMeta, setAlbumMeta] = useState(null);
  const [songs, setSongs] = useState([]);
  const [originalSongs, setOriginalSongs] = useState([]);
  const [artist, setArtist] = useState(null);
  const [comments, setComments] = useState([]);
  const [albumRating, setAlbumRating] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const { isAuthenticated, user } = useAuth();
  const [refreshData, setRefreshData] = useState(false);
  const [selectedSong, setSelectedSong] = useState(null);
  const [ratingSubmitted, setRatingSubmitted] = useState(false);
  
  // For the song rating dialog
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  // Add state for comment deletion
  const [commentToDelete, setCommentToDelete] = useState(null);
  const { isOpen: isDeleteDialogOpen, onOpen: openDeleteDialog, onClose: closeDeleteDialog } = useDisclosure();

  // Custom close handler for the rating dialog
  const handleCloseRatingDialog = () => {
    // If rating wasn't submitted, revert back to original songs state
    if (!ratingSubmitted) {
      // Find the original song state
      const originalSong = originalSongs.find(s => s.song_id === selectedSong.song_id);
      // Update the songs array with original rating
      setSongs(prevSongs => prevSongs.map(song => 
        song.song_id === selectedSong.song_id 
          ? { ...song, star: originalSong.star || 0 }
          : song
      ));
    }
    setRatingSubmitted(false); // Reset for next time
    onClose(); // Close the dialog
  };

  useEffect(() => {
    const fetchAlbumData = async () => {
      if (!id) return;
      
      try {
        setIsLoading(true);
        
        // Fetch album details
        const albumData = await api.getAlbum(id);
        setAlbum(albumData);
        
        // Fetch album rating
        try {
          const ratingData = await api.getAlbumRating(id);
          setAlbumRating(ratingData);
        } catch (ratingErr) {
          console.log('No rating available for this album');
        }
        
        // Fetch artist details
        try {
          const artistData = await api.getArtist(albumData.artist_id);
          setArtist(artistData);
        } catch (artistErr) {
          console.log('Failed to load artist details');
        }
        
        // Fetch album's songs with ratings
        try {
          // First get basic song data
          const songsData = await api.getAlbumSongs(id);
          
          // Then fetch individual song ratings and enhance the song objects
          const songsWithRatings = await Promise.all(
            songsData.map(async (song) => {
              try {
                const ratingData = await api.getSongRating(song.song_id);
                // Add the star rating (0-5 scale) to the song object
                return { 
                  ...song, 
                  star: ratingData.average_rating // This should be 0-5 scale already
                };
              } catch (error) {
                console.log(`No rating available for song ${song.song_id}`);
                return { ...song, star: 0 };
              }
            })
          );
          
          setSongs(songsWithRatings);
          setOriginalSongs([...songsWithRatings]);
        } catch (err) {
          console.error('Error fetching songs with ratings:', err);
          // Fallback to just songs without ratings
          const songsData = await api.getAlbumSongs(id);
          setSongs(songsData);
          setOriginalSongs([...songsData]);
        }
        
        // Try to fetch album metadata
        try {
          const metaData = await api.getAlbumMeta(id);
          setAlbumMeta(metaData);
        } catch (metaErr) {
          console.log('No metadata available for this album');
        }
        
        // Try to fetch album comments
        try {
          const commentsData = await api.getAlbumComments(id);
          
          // Enhance comments with user data if available
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
          console.log('No comments available for this album');
        }
        
      } catch (err) {
        console.error('Error fetching album data:', err);
        setError('Failed to load album details. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchAlbumData();
  }, [id, refreshData]);

  // Handler for submitting a new album comment with rating
  const handleAlbumCommentSubmit = async (comment, rating) => {
    try {
      await api.addAlbumComment(id, comment, rating);
      setRefreshData(prev => !prev); // Toggle to trigger a refresh
      toast({
        title: "Review submitted",
        description: "Your album review has been submitted successfully.",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Error submitting album comment:', error);
      toast({
        title: "Error",
        description: "Failed to submit your review. Please try again.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      throw error;
    }
  };

  // Handler for submitting a song rating
  const handleSongRating = async (rating, comment) => {
    if (!selectedSong) return;
    
    try {
      // The API expects a rating between 0-5, so don't convert it
      await api.addSongComment(selectedSong.song_id, comment, rating);
      
      // Refresh the page to get new average ratings
      setRefreshData(prev => !prev);
      
      setRatingSubmitted(true);
      toast({
        title: "Rating submitted",
        description: `Your rating for "${selectedSong.name}" has been submitted.`,
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      
      onClose();
      
    } catch (error) {
      console.error('Error submitting song rating:', error);
      throw new Error(error.message || "Failed to submit your rating. Please try again.");
    }
  };

  // Handler for opening the song rating dialog
  const handleOpenSongRating = (song) => {
    if (!isAuthenticated) {
      toast({
        title: "Login required",
        description: "You need to log in to rate songs.",
        status: "warning",
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    
    setSelectedSong({ ...song, star: Math.round(song.star) || 0 });
    setRatingSubmitted(false); // Reset submission status
    onOpen();
  };

  // Update the delete comment handler to work with the new dialog
  const handleDeleteComment = async () => {
    if (!commentToDelete) return;
    
    try {
      await api.deleteAlbumComment(commentToDelete.id);
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

  // Updated renderComments function to use the DeleteConfirmationDialog
  const renderComments = () => {
    return (
      <Box my={8}>
        <Heading size="md" mb={4}>Comments</Heading>
        
        {isAuthenticated && (
          <Box mb={6} p={4} bg="gray.50" borderRadius="md">
            <CommentForm
              onSubmit={handleAlbumCommentSubmit}
              showRating={true}
              maxChars={200}
              placeholder="Share your thoughts about this album (200 characters max)"
            />
          </Box>
        )}
        
        {comments.length === 0 ? (
          <Text py={4}>No comments yet. Be the first to comment!</Text>
        ) : (
          <VStack spacing={4} align="stretch">
            {comments.map((comment, index) => (
              <CommentItem
                key={index}
                comment={comment}
                currentUser={user}
                onDeleteClick={(comment) => {
                  setCommentToDelete(comment);
                  openDeleteDialog();
                }}
                formatDate={formatDate}
                variant="album"
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
    );
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
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
          <Text>Loading album details...</Text>
        </Box>
      );
    }

    if (!album) {
      return (
        <Box textAlign="center" py={10}>
          <Heading mb={4}>Album Not Found</Heading>
          <Text>The album you're looking for doesn't exist.</Text>
          <NextLink href="/albums" passHref legacyBehavior>
            <Link color="blue.500" mt={4} display="inline-block">
              Back to Albums
            </Link>
          </NextLink>
        </Box>
      );
    }

    return (
      <Box>
        <Box mb={8}>
          <Flex direction={{ base: 'column', md: 'row' }} gap={8}>
            <Box flexShrink={0} maxW={{ base: '100%', md: '300px' }}>
              <Image
                src={albumMeta?.pic_address || '/album-placeholder.svg'}
                alt={album.name}
                borderRadius="lg"
                width="260px"
                height="260px"
                objectFit="cover"
                crossOrigin="anonymous"
                fallbackSrc="/album-placeholder.svg"
              />
              <Flex justify="center" mt={2}>
                {albumRating && albumRating.average_rating > 0 ? 
                  <Flex align="center" gap={2}>
                    <StarRating rating={albumRating.stars} size="lg" />
                  </Flex>
                  : 
                  <StarRating rating={0} size="lg" />
                }
              </Flex>
            </Box>
            
            <Box>
              <Heading size="md" mb={4}>{album.name}</Heading>
              
              {artist && (
                <Flex gap={2} mb={4}>
                  <Text width="120px">Artist:</Text>
                  <NextLink href={`/artists/${artist.artist_id}`} passHref legacyBehavior>
                    <Link fontSize="md" color="blue.500">
                      {artist.name}
                    </Link>
                  </NextLink>
                </Flex>
              )}
              
              <Box mt={4}>
                <VStack spacing={2} align="flex-start">
                  <Flex>
                    <Text width="120px">Release Date:</Text>
                    <Text>{formatDate(album.release_date)}</Text>
                  </Flex>
                  
                  <Flex>
                    <Text width="120px">Language:</Text>
                    <Text>{album.album_lan}</Text>
                  </Flex>
                  
                  <Flex>
                    <Text width="120px">Category:</Text>
                    <Text>{album.album_category}</Text>
                  </Flex>
                  
                  <Flex>
                    <Text width="120px">Rating:</Text>
                    <Text>{albumRating && albumRating.average_rating > 0 ? albumRating.average_rating : "No rating now"}</Text>
                  </Flex>
                  
                  {album.record_label && album.record_label !== "''" && (
                    <Flex>
                      <Text fontWeight="bold" width="120px">Record Label:</Text>
                      <Text>{album.record_label}</Text>
                    </Flex>
                  )}
                </VStack>
              </Box>
              
              {albumMeta && albumMeta.info && (
                <Box mt={6} mb={4}>
                  <Heading as="h3" size="md" mb={3}>Description</Heading>
                  <Text fontSize="md" lineHeight="1.7" px={3} py={4} bg="gray.50" borderRadius="md">
                    {albumMeta.info}
                  </Text>
                </Box>
              )}
              
              <Divider my={4} />
            </Box>
          </Flex>
        </Box>
        
        {/* Songs Section */}
        <Box mt={8} mb={8}>
          <SectionHeader title={`Songs (${songs.length})`} />
          
          {songs.length === 0 ? (
            <Text py={4}>No songs available for this album.</Text>
          ) : (
            <Box mt={4}>
              <Table variant="simple" size="md">
                <Thead>
                  <Tr borderBottom="1px solid" borderColor="gray.200">
                    <Th width="60px" textAlign="center" fontWeight="normal" fontSize="sm" color="gray.500" py={3}>#</Th>
                    <Th fontWeight="normal" fontSize="sm" color="gray.500" py={3}>Song</Th>
                    <Th width="120px" fontWeight="normal" fontSize="sm" color="gray.500" py={3}>Rating</Th>
                    <Th fontWeight="normal" fontSize="sm" color="gray.500" py={3}>Artist</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {songs.map((song) => (
                    <Tr key={song.song_id}>
                      <Td textAlign="center">{song.order}</Td>
                      <Td>
                        <NextLink href={`/songs/${song.song_id}`} passHref legacyBehavior>
                          <Link fontWeight="medium" color="blue.600" _hover={{ textDecoration: 'underline' }}>
                            {song.name}
                          </Link>
                        </NextLink>
                      </Td>
                      <Td>
                        {isAuthenticated ? (
                          <Box cursor="pointer">
                            <InteractiveStarRating
                              initialRating={Math.round(song.star) || 0}
                              size="sm"
                              onRatingSelect={(newRating) => {
                                setSelectedSong({ ...song, star: newRating });
                                onOpen();
                              }}
                              resetOnClick={true}
                            />
                          </Box>
                        ) : (
                          <StarRating rating={Math.round(song.star) || 0} size="sm" />
                        )}
                      </Td>
                      <Td>
                        <NextLink href={`/artists/${song.artist_id}`} passHref legacyBehavior>
                          <Link color="gray.600">
                            {song.artist_name}
                          </Link>
                        </NextLink>
                      </Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            </Box>
          )}
        </Box>
        
        {/* Render Comments Section */}
        {renderComments()}
      </Box>
    );
  };

  return (
    <XiamiuLayout>
      <Box maxW="1200px" mx="auto" px={4} py={8}>
        {renderContent()}
      </Box>
      
      {/* Song Rating Dialog */}
      {selectedSong && (
        <SongRatingDialog
          isOpen={isOpen}
          onClose={handleCloseRatingDialog}
          songName={selectedSong.name}
          initialRating={selectedSong.star}
          onSubmit={handleSongRating}
        />
      )}
    </XiamiuLayout>
  );
}