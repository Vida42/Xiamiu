import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/router';
import NextLink from 'next/link';
import { Box, Heading, Text, Image, SimpleGrid, Flex, Badge, Link, Divider, useColorModeValue, Button, VStack, useToast, AlertDialog, AlertDialogBody, AlertDialogFooter, AlertDialogHeader, AlertDialogContent, AlertDialogOverlay, useDisclosure, HStack, Avatar } from '@chakra-ui/react';
import { api } from '../../utils/api';
import { AlbumCard, CollectionCard } from '../../components/Cards';
import XiamiuLayout from '../../components/Layout/XiamiuLayout';
import { CommentForm, CommentItem, DeleteConfirmationDialog } from '../../components';
import { useAuth } from '../../contexts/AuthContext';

// Reusable SectionHeader component similar to the one in index.js
const SectionHeader = ({ title }) => {
  return (
    <Flex justify="space-between" align="center" mb={4}>
      <Flex align="center">
        <Heading 
          size="md" 
          fontFamily="'Microsoft YaHei', 'STHeiti', sans-serif"
          color="black"
          fontWeight="bold"
        >
          {title}
        </Heading>
      </Flex>
    </Flex>
  );
};

export default function ArtistDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [artist, setArtist] = useState(null);
  const [artistMeta, setArtistMeta] = useState(null);
  const [albums, setAlbums] = useState([]);
  const [filteredAlbums, setFilteredAlbums] = useState([]);
  const [displayedAlbums, setDisplayedAlbums] = useState([]);
  const [songs, setSongs] = useState([]);
  const [comments, setComments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [activeCategoryFilter, setActiveCategoryFilter] = useState('All');
  
  // Collections data
  const [songsByStarRating, setSongsByStarRating] = useState({
    5: [],
    4: [],
    3: [],
    2: [],
    1: []
  });

  // Pagination for albums
  const albumsPerPage = 8;
  const [currentPage, setCurrentPage] = useState(1);

  const albumCategories = [
    { value: 'All', label: '全部' },
    { value: 'Studio', label: '录音室专辑' },
    { value: 'Compilation', label: '精选集' },
    { value: 'Live', label: '现场专辑' },
    { value: 'EP', label: 'EP/单曲' }
  ];

  const { isAuthenticated, user } = useAuth();
  const [refreshComments, setRefreshComments] = useState(false);
  const toast = useToast();
  const [commentToDelete, setCommentToDelete] = useState(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const cancelRef = useRef();

  useEffect(() => {
    const fetchArtistData = async () => {
      if (!id) return;
      
      try {
        setIsLoading(true);
        
        // Fetch artist details
        const artistData = await api.getArtist(id);
        setArtist(artistData);
        
        // Fetch artist's albums
        const albumsData = await api.getArtistAlbums(id);
        setAlbums(albumsData);
        setFilteredAlbums(albumsData);
        
        // Try to fetch artist metadata
        try {
          const metaData = await api.getArtistMeta(id);
          setArtistMeta(metaData);
        } catch (metaErr) {
          console.log('No metadata available for this artist');
        }
        
        // Try to fetch artist comments
        try {
          const commentsData = await api.getArtistComments(id);
          
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
          console.log('No comments available for this artist');
        }
        
        // Fetch all songs from all albums to create collections
        try {
          const allSongs = [];
          for (const album of albumsData) {
            const albumSongs = await api.getAlbumSongs(album.album_id);
            allSongs.push(...albumSongs);
          }
          setSongs(allSongs);
          
          // Group songs by star rating
          const groupedSongs = {
            5: [],
            4: [],
            3: [],
            2: [],
            1: []
          };
          
          allSongs.forEach(song => {
            if (song.star >= 1 && song.star <= 5) {
              groupedSongs[song.star].push(song);
            }
          });
          
          setSongsByStarRating(groupedSongs);
        } catch (songsErr) {
          console.log('Error fetching songs for collections', songsErr);
        }
        
      } catch (err) {
        console.error('Error fetching artist data:', err);
        setError('Failed to load artist details. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchArtistData();
  }, [id, refreshComments]);

  // Filter albums based on selected category
  useEffect(() => {
    if (activeCategoryFilter === 'All') {
      setFilteredAlbums(albums);
    } else {
      const filtered = albums.filter(album => album.album_category === activeCategoryFilter);
      setFilteredAlbums(filtered);
    }
  }, [activeCategoryFilter, albums]);

  // Filter albums based on selected tab
  useEffect(() => {
    let sorted = [...albums];
    if (activeTab === 1) { // Sort by rating
      sorted.sort((a, b) => b.star - a.star);
    } else if (activeTab === 0) { // Default sorting (by release date)
      sorted.sort((a, b) => new Date(b.release_date) - new Date(a.release_date));
    }
    
    // Apply category filter
    if (activeCategoryFilter !== 'All') {
      sorted = sorted.filter(album => album.album_category === activeCategoryFilter);
    }
    
    setFilteredAlbums(sorted);
    // Reset to first page when sort changes
    setCurrentPage(1);
  }, [activeTab, albums, activeCategoryFilter]);

  // Update displayed albums based on pagination
  useEffect(() => {
    const startIndex = (currentPage - 1) * albumsPerPage;
    const endIndex = startIndex + albumsPerPage;
    setDisplayedAlbums(filteredAlbums.slice(startIndex, endIndex));
  }, [filteredAlbums, currentPage, albumsPerPage]);

  const renderCategoryFilters = () => {
    const activeBg = useColorModeValue('black', 'gray.900');
    const inactiveBg = useColorModeValue('gray.100', 'gray.700');
    const activeColor = useColorModeValue('white', 'white');
    const inactiveColor = useColorModeValue('gray.800', 'gray.100');
    
    return (
      <Flex 
        justifyContent="center" 
        flexWrap="wrap" 
        gap={3} 
        mt={2} 
        mb={6}
      >
        {albumCategories.map(category => (
          <Box
            key={category.value}
            px={4}
            py={2}
            bg={activeCategoryFilter === category.value ? activeBg : inactiveBg}
            color={activeCategoryFilter === category.value ? activeColor : inactiveColor}
            cursor="pointer"
            rounded="md"
            fontSize="sm"
            fontWeight={activeCategoryFilter === category.value ? 'bold' : 'normal'}
            onClick={() => setActiveCategoryFilter(category.value)}
            _hover={{
              bg: activeCategoryFilter === category.value ? activeBg : 'gray.200',
            }}
            textAlign="center"
          >
            {category.label}
          </Box>
        ))}
      </Flex>
    );
  };

  const renderPagination = () => {
    const totalPages = Math.ceil(filteredAlbums.length / albumsPerPage);
    if (totalPages <= 1) return null;

    return (
      <Flex justify="center" mt={6} gap={2}>
        <Button 
          size="sm" 
          onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
          isDisabled={currentPage === 1}
          colorScheme="orange"
          variant="outline"
        >
          Previous
        </Button>
        <Text alignSelf="center" fontSize="sm">
          Page {currentPage} of {totalPages}
        </Text>
        <Button 
          size="sm" 
          onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
          isDisabled={currentPage === totalPages}
          colorScheme="orange"
          variant="outline"
        >
          Next
        </Button>
      </Flex>
    );
  };

  // Handler for submitting a new artist comment
  const handleCommentSubmit = async (comment) => {
    try {
      await api.addArtistComment(id, comment);
      setRefreshComments(prev => !prev); // Toggle to trigger a refresh
      
      // Show success toast
      toast({
        title: "Comment submitted",
        description: "Your comment has been added successfully.",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      
    } catch (error) {
      console.error('Error submitting artist comment:', error);
      
      // Show error toast with the error message
      toast({
        title: "Error",
        description: error.message || "Failed to submit your comment. Please try again.",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
      
      throw error;
    }
  };

  // Update the handleDeleteComment function
  const handleDeleteComment = async () => {
    if (!commentToDelete) return;
    
    try {
      await api.deleteArtistComment(commentToDelete.id);
      // Update the local state to remove the deleted comment
      setComments(comments.filter(comment => comment.id !== commentToDelete.id));
      toast({
        title: "Comment deleted",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Error deleting comment:', error);
      toast({
        title: "Error",
        description: "Failed to delete comment. Please try again.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    } finally {
      onClose();
      setCommentToDelete(null);
    }
  };

  // Function to render comments section
  const renderComments = () => {
    return (
      <Box my={8}>
        <SectionHeader title="Comments" />
        
        {isAuthenticated && (
          <Box mb={6} p={4} bg="gray.50" borderRadius="md">
            <CommentForm
              onSubmit={handleCommentSubmit}
              showRating={false}
              maxChars={200}
              placeholder="Share your thoughts about this artist (200 characters max)"
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
                  onOpen();
                }}
                variant="artist"
              />
            ))}
          </VStack>
        )}
        <DeleteConfirmationDialog 
          isOpen={isOpen}
          onClose={onClose}
          onDelete={handleDeleteComment}
        />
      </Box>
    );
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
          <Text>Loading artist details...</Text>
        </Box>
      );
    }

    if (!artist) {
      return (
        <Box textAlign="center" py={10}>
          <Heading mb={4}>Artist Not Found</Heading>
          <Text>The artist you're looking for doesn't exist.</Text>
          <NextLink href="/artists" passHref legacyBehavior>
            <Link color="blue.500" mt={4} display="inline-block">
              Back to Artists
            </Link>
          </NextLink>
        </Box>
      );
    }

    // Check if there are any songs with star ratings
    const hasCollections = Object.values(songsByStarRating).some(songs => songs.length > 0);

    return (
      <Box>
        <Box mb={8}>
          <Flex direction={{ base: 'column', md: 'row' }} gap={8}>
            <Box flexShrink={0} maxW={{ base: '100%', md: '300px' }}>
              <Image
                src={artistMeta?.pic_address || '/album-placeholder.svg'}
                alt={artist.name}
                borderRadius="lg"
                width="100%"
                height="auto"
                objectFit="cover"
                crossOrigin="anonymous"
                fallbackSrc="/album-placeholder.svg"
              />
            </Box>
            
            <Box>
              <Heading size="md" mb={4}>{artist.name}</Heading>
              <Text fontSize="md" color="gray.600" mb={4}>
                Region: {artist.region}
              </Text>
              
              {artistMeta && artistMeta.info && (
                <Box mt={6} mb={6}>
                  <Text fontWeight="bold" size="md" mb={3}>Description</Text>
                  <Text fontSize="md" lineHeight="1.7" px={3} py={4} borderRadius="md">
                    {artistMeta.info}
                  </Text>
                </Box>
              )}
              
              <Divider my={4} />
            </Box>
          </Flex>
        </Box>
        
        {/* Albums section with SectionHeader */}
        <Box mt={12}>
          <SectionHeader title={`${artist.name} Discography (${albums.length})`} />
          
          <Box 
            className="detail-tabs"
            mt={4}
          >
            <Flex 
              as="ul" 
              className="bottom-ul-menu"
              mb={4}
            >
              <Box as="li" className={activeTab === 0 ? "active" : ""}>
                <Link onClick={() => setActiveTab(0)}>
                  Release Date
                </Link>
              </Box>
              <Box as="li" className={activeTab === 1 ? "active" : ""}>
                <Link onClick={() => setActiveTab(1)}>
                  Rating
                </Link>
              </Box>
              <Box as="li" className={activeTab === 2 ? "active" : ""}>
                <Link onClick={() => setActiveTab(2)}>
                  Album Type
                </Link>
              </Box>
            </Flex>
            
            {/* Show category filters only when "Album Type" tab is active */}
            {activeTab === 2 && renderCategoryFilters()}
            
            <Box p={4}>
              {filteredAlbums.length === 0 ? (
                <Text>No albums found for this artist.</Text>
              ) : (
                <>
                  <SimpleGrid columns={{ base: 1, md: 3, lg: 4 }} spacing={3}>
                    {displayedAlbums.map(album => (
                      <AlbumCard key={album.album_id} album={album} />
                    ))}
                  </SimpleGrid>
                  {renderPagination()}
                </>
              )}
            </Box>
          </Box>
        </Box>
        
        {/* Collections section with SectionHeader - only show if there are collections */}
        {hasCollections && (
          <Box mt={12}>
            <SectionHeader 
              title={`${artist.name} Collections`} 
            />
            
            <Box p={4}>
              <SimpleGrid columns={{ base: 2, md: 3, lg: 5 }} spacing={4}>
                {[5, 4, 3, 2, 1].map(starRating => {
                  const songsCount = songsByStarRating[starRating]?.length || 0;
                  // Only show collections that have at least one song
                  return songsCount > 0 ? (
                    <CollectionCard 
                      key={starRating} 
                      artistId={id} 
                      starRating={starRating} 
                      songCount={songsCount} 
                    />
                  ) : null;
                }).filter(Boolean)}
              </SimpleGrid>
            </Box>
          </Box>
        )}
        
        {/* Comments section with SectionHeader */}
        {renderComments()}
      </Box>
    );
  };

  return (
    <XiamiuLayout>
      {renderContent()}
    </XiamiuLayout>
  );
} 