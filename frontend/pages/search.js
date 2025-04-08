import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { Heading, Text, SimpleGrid, Box, Divider, Tabs, TabList, TabPanels, Tab, TabPanel, Flex, Link } from '@chakra-ui/react';
import { api } from '../utils/api';
import { ArtistCard, AlbumCard, SongCard } from '../components/Cards';
import XiamiuLayout from '../components/Layout/XiamiuLayout';

export default function Search() {
  const router = useRouter();
  const { q, type } = router.query;
  const [searchResults, setSearchResults] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTabIndex, setActiveTabIndex] = useState(0);

  useEffect(() => {
    const fetchSearchResults = async () => {
      if (!q) return;
      
      try {
        setIsLoading(true);
        const results = await api.search(q);
        setSearchResults(results);
        
        // Set the active tab based on search type
        if (type) {
          switch (type) {
            case 'artist':
              setActiveTabIndex(1);
              break;
            case 'album':
              setActiveTabIndex(2);
              break;
            case 'song':
              setActiveTabIndex(3);
              break;
            default:
              setActiveTabIndex(0);
          }
        }
      } catch (err) {
        console.error('Error searching:', err);
        setError('An error occurred while searching. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSearchResults();
  }, [q, type]);

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
          <Heading mb={4}>Searching for "{q}"{type ? ` in ${type}s` : ''}</Heading>
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
          <Text fontSize="lg">No results found for "{q}"{type ? ` in ${type}s` : ''}</Text>
          <Text mt={2}>Try searching for something else.</Text>
        </Box>
      );
    }

    // Filter results based on type if specified
    let filteredResults = { ...searchResults };
    if (type === 'artist') {
      filteredResults = { 
        artists: searchResults.artists, 
        albums: [], 
        songs: [] 
      };
    } else if (type === 'album') {
      filteredResults = { 
        artists: [], 
        albums: searchResults.albums, 
        songs: [] 
      };
    } else if (type === 'song') {
      filteredResults = { 
        artists: [], 
        albums: [], 
        songs: searchResults.songs 
      };
    }

    return (
      <Box>
        <Heading mb={6}>Search Results for "{q}"{type ? ` in ${type}s` : ''}</Heading>
        
        <Flex 
          as="ul" 
          className="bottom-ul-menu"
          mb={6}
        >
          <Box as="li" className={activeTabIndex === 0 ? "active" : ""}>
            <Link onClick={() => setActiveTabIndex(0)}>
              All Results
            </Link>
          </Box>
          <Box as="li" className={activeTabIndex === 1 ? "active" : ""}>
            <Link onClick={() => setActiveTabIndex(1)}>
              Artists ({searchResults.artists?.length || 0})
            </Link>
          </Box>
          <Box as="li" className={activeTabIndex === 2 ? "active" : ""}>
            <Link onClick={() => setActiveTabIndex(2)}>
              Albums ({searchResults.albums?.length || 0})
            </Link>
          </Box>
          <Box as="li" className={activeTabIndex === 3 ? "active" : ""}>
            <Link onClick={() => setActiveTabIndex(3)}>
              Songs ({searchResults.songs?.length || 0})
            </Link>
          </Box>
        </Flex>

        {activeTabIndex === 0 && (
          <Box>
            {filteredResults.artists?.length > 0 && (
              <Box mb={8}>
                <Heading size="md" mb={4}>Artists</Heading>
                <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
                  {filteredResults.artists.map(artist => (
                    <ArtistCard key={artist.artist_id} artist={artist} />
                  ))}
                </SimpleGrid>
                <Divider my={6} />
              </Box>
            )}

            {filteredResults.albums?.length > 0 && (
              <Box mb={8}>
                <Heading size="md" mb={4}>Albums</Heading>
                <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
                  {filteredResults.albums.map(album => (
                    <AlbumCard key={album.album_id} album={album} />
                  ))}
                </SimpleGrid>
                <Divider my={6} />
              </Box>
            )}

            {filteredResults.songs?.length > 0 && (
              <Box>
                <Heading size="md" mb={4}>Songs</Heading>
                <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
                  {filteredResults.songs.map(song => (
                    <SongCard key={song.song_id} song={song} />
                  ))}
                </SimpleGrid>
              </Box>
            )}
          </Box>
        )}

        {activeTabIndex === 1 && (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
            {searchResults.artists?.map(artist => (
              <ArtistCard key={artist.artist_id} artist={artist} />
            ))}
          </SimpleGrid>
        )}

        {activeTabIndex === 2 && (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
            {searchResults.albums?.map(album => (
              <AlbumCard key={album.album_id} album={album} />
            ))}
          </SimpleGrid>
        )}

        {activeTabIndex === 3 && (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
            {searchResults.songs?.map(song => (
              <SongCard key={song.song_id} song={song} />
            ))}
          </SimpleGrid>
        )}
      </Box>
    );
  };

  return (
    <XiamiuLayout>
      {renderContent()}
    </XiamiuLayout>
  );
} 