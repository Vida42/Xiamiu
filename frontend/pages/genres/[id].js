import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import NextLink from 'next/link';
import { Box, Heading, Text, SimpleGrid, Tabs, TabList, Tab, TabPanels, TabPanel, Flex, Link, Divider } from '@chakra-ui/react';
import { api } from '../../utils/api';
import { ArtistCard, AlbumCard } from '../../components/Cards';
import XiamiuLayout from '../../components/Layout/XiamiuLayout';

export default function GenreDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [genre, setGenre] = useState(null);
  const [relatedArtists, setRelatedArtists] = useState([]);
  const [relatedAlbums, setRelatedAlbums] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    const fetchGenreData = async () => {
      if (!id) return;
      
      try {
        setIsLoading(true);
        
        // Fetch genre details
        const genreData = await api.getGenre(id);
        setGenre(genreData);
        
        // Fetch related artists
        try {
          const artistsData = await api.getArtistsByGenre(id);
          setRelatedArtists(artistsData);
        } catch (artistErr) {
          console.error('Error fetching artists by genre:', artistErr);
          setRelatedArtists([]);
        }
        
        // Fetch related albums
        try {
          const albumsData = await api.getAlbumsByGenre(id);
          setRelatedAlbums(albumsData);
        } catch (albumErr) {
          console.error('Error fetching albums by genre:', albumErr);
          setRelatedAlbums([]);
        }
        
      } catch (err) {
        console.error('Error fetching genre data:', err);
        setError('Failed to load genre details. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchGenreData();
  }, [id]);

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
          <Box p={6} borderRadius="lg">
            <Heading size="lg" mb={4} color="gray.800">{genre.name}</Heading>
            <Text fontSize="md" mb={6}>{genre.info}</Text>
            
            <Divider my={4} borderColor="gray.200" />
          </Box>
        </Box>
        
        <Box 
          className="detail-tabs"
          mt={8}
        >
          <Flex 
            as="ul" 
            className="bottom-ul-menu"
            mb={4}
          >
            <Box as="li" className={activeTab === 0 ? "active" : ""}>
              <Link onClick={() => setActiveTab(0)}>
                Artists
              </Link>
            </Box>
            <Box as="li" className={activeTab === 1 ? "active" : ""}>
              <Link onClick={() => setActiveTab(1)}>
                Albums
              </Link>
            </Box>
          </Flex>
            
          {activeTab === 0 ? (
            <Box>
              {relatedArtists.length === 0 ? (
                <Box py={4}>
                  <Text>No artists available for this genre.</Text>
                  <Text fontSize="sm" color="gray.500" mt={2}>
                    This is a placeholder. In a complete implementation, this would show artists in this genre.
                  </Text>
                </Box>
              ) : (
                <SimpleGrid columns={{ base: 1, md: 3, lg: 5 }} spacing={3} mt={4}>
                  {relatedArtists.map(artist => (
                    <ArtistCard key={artist.artist_id} artist={artist} />
                  ))}
                </SimpleGrid>
              )}
            </Box>
          ) : (
            <Box>
              {relatedAlbums.length === 0 ? (
                <Box py={4}>
                  <Text>No albums available for this genre.</Text>
                  <Text fontSize="sm" color="gray.500" mt={2}>
                    This is a placeholder. In a complete implementation, this would show albums in this genre.
                  </Text>
                </Box>
              ) : (
                <SimpleGrid columns={{ base: 1, md: 3, lg: 5 }} spacing={3} mt={4}>
                  {relatedAlbums.map(album => (
                    <AlbumCard key={album.album_id} album={album} />
                  ))}
                </SimpleGrid>
              )}
            </Box>
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