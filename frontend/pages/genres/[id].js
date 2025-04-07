import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import NextLink from 'next/link';
import { Box, Heading, Text, SimpleGrid, Tabs, TabList, Tab, TabPanels, TabPanel, Flex, Link, Divider } from '@chakra-ui/react';
import { api } from '../../utils/api';
import { ArtistCard, AlbumCard } from '../../components/Cards';

export default function GenreDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [genre, setGenre] = useState(null);
  const [relatedArtists, setRelatedArtists] = useState([]);
  const [relatedAlbums, setRelatedAlbums] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchGenreData = async () => {
      if (!id) return;
      
      try {
        setIsLoading(true);
        
        // Fetch genre details
        const genreData = await api.getGenre(id);
        setGenre(genreData);
        
        // In a real app, you would have API endpoints to fetch artists and albums by genre
        // For demonstration purposes, we're just showing placeholders
        
        // TODO: Add API endpoint to fetch artists by genre ID
        setRelatedArtists([]);
        
        // TODO: Add API endpoint to fetch albums by genre ID
        setRelatedAlbums([]);
        
      } catch (err) {
        console.error('Error fetching genre data:', err);
        setError('Failed to load genre details. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchGenreData();
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
        <Text>Loading genre details...</Text>
      </Box>
    );
  }

  if (!genre) {
    return (
      <Box textAlign="center" py={10}>
        <Heading mb={4}>Genre Not Found</Heading>
        <Text>The genre you're looking for doesn't exist.</Text>
        <NextLink href="/genres" passHref legacyBehavior>
          <Link color="blue.500" mt={4} display="inline-block">
            Back to Genres
          </Link>
        </NextLink>
      </Box>
    );
  }

  return (
    <Box>
      <Box mb={8}>
        <Box p={6} borderRadius="lg" bg="purple.50">
          <Heading size="2xl" mb={4} color="purple.700">{genre.name}</Heading>
          <Text fontSize="lg" mb={6}>{genre.info}</Text>
          
          <Divider my={4} borderColor="purple.200" />
          
          <NextLink href="/genres" passHref legacyBehavior>
            <Link color="blue.500">
              Back to All Genres
            </Link>
          </NextLink>
        </Box>
      </Box>
      
      <Tabs isLazy colorScheme="purple" mt={8}>
        <TabList>
          <Tab>Artists</Tab>
          <Tab>Albums</Tab>
        </TabList>
        
        <TabPanels>
          <TabPanel>
            {relatedArtists.length === 0 ? (
              <Box py={4}>
                <Text>No artists available for this genre.</Text>
                <Text fontSize="sm" color="gray.500" mt={2}>
                  This is a placeholder. In a complete implementation, this would show artists in this genre.
                </Text>
              </Box>
            ) : (
              <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6} mt={4}>
                {relatedArtists.map(artist => (
                  <ArtistCard key={artist.artist_id} artist={artist} />
                ))}
              </SimpleGrid>
            )}
          </TabPanel>
          
          <TabPanel>
            {relatedAlbums.length === 0 ? (
              <Box py={4}>
                <Text>No albums available for this genre.</Text>
                <Text fontSize="sm" color="gray.500" mt={2}>
                  This is a placeholder. In a complete implementation, this would show albums in this genre.
                </Text>
              </Box>
            ) : (
              <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6} mt={4}>
                {relatedAlbums.map(album => (
                  <AlbumCard key={album.album_id} album={album} />
                ))}
              </SimpleGrid>
            )}
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
} 