import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import NextLink from 'next/link';
import { Box, Heading, Text, Image, SimpleGrid, Tabs, TabList, Tab, TabPanels, TabPanel, Flex, Badge, Link, Divider } from '@chakra-ui/react';
import { api } from '../../utils/api';
import { AlbumCard } from '../../components/Cards';

export default function ArtistDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [artist, setArtist] = useState(null);
  const [artistMeta, setArtistMeta] = useState(null);
  const [albums, setAlbums] = useState([]);
  const [comments, setComments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

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
              src={artistMeta?.pic_address || '/placeholder-artist.jpg'}
              alt={artist.name}
              borderRadius="lg"
              width="100%"
              height="auto"
              objectFit="cover"
              crossOrigin="anonymous"
              fallbackSrc="/placeholder-artist.jpg"
            />
          </Box>
          
          <Box>
            <Heading size="2xl" mb={2}>{artist.name}</Heading>
            <Text fontSize="lg" color="gray.600" mb={4}>
              Reign: {artist.reign}
            </Text>
            
            {artistMeta && artistMeta.info && (
              <Box mt={6} mb={6}>
                <Heading as="h3" size="md" mb={3}>Description</Heading>
                <Text fontSize="md" lineHeight="1.7" px={3} py={4} bg="gray.50" borderRadius="md">
                  {artistMeta.info}
                </Text>
              </Box>
            )}
            
            <Divider my={4} />
            
            <NextLink href="/artists" passHref legacyBehavior>
              <Link color="blue.500">
                Back to All Artists
              </Link>
            </NextLink>
          </Box>
        </Flex>
      </Box>
      
      <Tabs isLazy colorScheme="blue" mt={8}>
        <TabList>
          <Tab>Albums ({albums.length})</Tab>
          <Tab>Comments ({comments.length})</Tab>
        </TabList>
        
        <TabPanels>
          <TabPanel>
            {albums.length === 0 ? (
              <Text py={4}>No albums available for this artist.</Text>
            ) : (
              <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6} mt={4}>
                {albums.map(album => (
                  <AlbumCard key={album.album_id} album={album} />
                ))}
              </SimpleGrid>
            )}
          </TabPanel>
          
          <TabPanel>
            {comments.length === 0 ? (
              <Text py={4}>No comments available for this artist.</Text>
            ) : (
              <Box mt={4}>
                {comments.map(comment => (
                  <Box 
                    key={comment.id} 
                    p={4} 
                    borderWidth="1px" 
                    borderRadius="md"
                    mb={4}
                  >
                    <Text>{comment.comment}</Text>
                    <Flex mt={2} justify="space-between" alignItems="center">
                      <Text fontSize="sm" color="gray.500">
                        Posted on {new Date(comment.review_date).toLocaleDateString()}
                      </Text>
                      <Badge colorScheme="green">
                        {comment.num_like} likes
                      </Badge>
                    </Flex>
                  </Box>
                ))}
              </Box>
            )}
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
} 