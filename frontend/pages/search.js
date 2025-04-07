import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { Heading, Text, SimpleGrid, Box, Divider, Tabs, TabList, TabPanels, Tab, TabPanel } from '@chakra-ui/react';
import { api } from '../utils/api';
import { ArtistCard, AlbumCard, SongCard } from '../components/Cards';
import XiamiuLayout from '../components/Layout/XiamiuLayout';

export default function Search() {
  const router = useRouter();
  const { q } = router.query;
  const [searchResults, setSearchResults] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSearchResults = async () => {
      if (!q) return;
      
      try {
        setIsLoading(true);
        const results = await api.search(q);
        setSearchResults(results);
      } catch (err) {
        console.error('Error searching:', err);
        setError('An error occurred while searching. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSearchResults();
  }, [q]);

  const renderContent = () => {
    if (!q) {
      return (
        <Box textAlign="center" py={10}>
          <Heading mb={4}>No search query provided</Heading>
          <Text>Please enter a search term to find artists, albums, and songs.</Text>
        </Box>
      );
    }

    if (error) {
      return (
        <Box textAlign="center" py={10}>
          <Heading mb={4}>Search Error</Heading>
          <Text>{error}</Text>
        </Box>
      );
    }

    if (isLoading) {
      return (
        <Box textAlign="center" py={10}>
          <Heading mb={4}>Searching for "{q}"</Heading>
          <Text>Loading results...</Text>
        </Box>
      );
    }

    const hasResults = 
      searchResults && (
        searchResults.artists?.length > 0 || 
        searchResults.albums?.length > 0 || 
        searchResults.songs?.length > 0
      );

    if (!hasResults) {
      return (
        <Box textAlign="center" py={10}>
          <Text fontSize="lg">No results found for "{q}"</Text>
          <Text mt={2}>Try searching for something else.</Text>
        </Box>
      );
    }

    return (
      <Box>
        <Heading mb={6}>Search Results for "{q}"</Heading>
        
        <Tabs isLazy>
          <TabList>
            <Tab>All Results</Tab>
            <Tab>Artists ({searchResults.artists?.length || 0})</Tab>
            <Tab>Albums ({searchResults.albums?.length || 0})</Tab>
            <Tab>Songs ({searchResults.songs?.length || 0})</Tab>
          </TabList>

          <TabPanels>
            <TabPanel>
              {searchResults.artists?.length > 0 && (
                <Box mb={8}>
                  <Heading size="md" mb={4}>Artists</Heading>
                  <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
                    {searchResults.artists.map(artist => (
                      <ArtistCard key={artist.artist_id} artist={artist} />
                    ))}
                  </SimpleGrid>
                  <Divider my={6} />
                </Box>
              )}

              {searchResults.albums?.length > 0 && (
                <Box mb={8}>
                  <Heading size="md" mb={4}>Albums</Heading>
                  <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
                    {searchResults.albums.map(album => (
                      <AlbumCard key={album.album_id} album={album} />
                    ))}
                  </SimpleGrid>
                  <Divider my={6} />
                </Box>
              )}

              {searchResults.songs?.length > 0 && (
                <Box>
                  <Heading size="md" mb={4}>Songs</Heading>
                  <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
                    {searchResults.songs.map(song => (
                      <SongCard key={song.song_id} song={song} />
                    ))}
                  </SimpleGrid>
                </Box>
              )}
            </TabPanel>

            <TabPanel>
              <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
                {searchResults.artists?.map(artist => (
                  <ArtistCard key={artist.artist_id} artist={artist} />
                ))}
              </SimpleGrid>
            </TabPanel>

            <TabPanel>
              <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
                {searchResults.albums?.map(album => (
                  <AlbumCard key={album.album_id} album={album} />
                ))}
              </SimpleGrid>
            </TabPanel>

            <TabPanel>
              <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
                {searchResults.songs?.map(song => (
                  <SongCard key={song.song_id} song={song} />
                ))}
              </SimpleGrid>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </Box>
    );
  };

  return (
    <XiamiuLayout>
      {renderContent()}
    </XiamiuLayout>
  );
} 