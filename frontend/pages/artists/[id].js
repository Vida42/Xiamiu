import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import NextLink from 'next/link';
import { Box, Heading, Text, Image, SimpleGrid, Tabs, TabList, Tab, TabPanels, TabPanel, Flex, Badge, Link, Divider, HStack, useColorModeValue } from '@chakra-ui/react';
import { api } from '../../utils/api';
import { AlbumCard } from '../../components/Cards';
import XiamiuLayout from '../../components/Layout/XiamiuLayout';

// Reusable SectionHeader component similar to the one in index.js
const SectionHeader = ({ title }) => {
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
  const [comments, setComments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [activeCategoryFilter, setActiveCategoryFilter] = useState('All');

  const albumCategories = [
    { value: 'All', label: '全部' },
    { value: 'Studio', label: '录音室专辑' },
    { value: 'Compilation', label: '精选集' },
    { value: 'Live', label: '现场专辑' },
    { value: 'EP', label: 'EP/单曲' }
  ];

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
          setComments(commentsData);
        } catch (commentsErr) {
          console.log('No comments available for this artist');
        }
        
      } catch (err) {
        console.error('Error fetching artist data:', err);
        setError('Failed to load artist details. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchArtistData();
  }, [id]);

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
  }, [activeTab, albums, activeCategoryFilter]);

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
                Reign: {artist.reign}
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
                <SimpleGrid columns={{ base: 1, md: 3, lg: 4 }} spacing={3}>
                  {filteredAlbums.map(album => (
                    <AlbumCard key={album.album_id} album={album} />
                  ))}
                </SimpleGrid>
              )}
            </Box>
          </Box>
        </Box>
        
        {/* Comments section with SectionHeader */}
        <Box mt={12} mb={8}>
          <SectionHeader title="Comments" />
          
          {comments.length === 0 ? (
            <Text py={4}>No comments available for this artist.</Text>
          ) : (
            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4} mt={4}>
              {comments.map(comment => (
                <Box 
                  key={comment.id} 
                  p={4} 
                  borderWidth="1px" 
                  borderRadius="md"
                  borderColor="gray.200"
                >
                  <Text>{comment.comment}</Text>
                  <Flex mt={2} justify="space-between" alignItems="center">
                    <Text fontSize="sm" color="gray.500">
                      Posted on {new Date(comment.review_date).toLocaleDateString()}
                    </Text>
                    <Badge colorScheme="orange">
                      {comment.num_like} likes
                    </Badge>
                  </Flex>
                </Box>
              ))}
            </SimpleGrid>
          )}
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