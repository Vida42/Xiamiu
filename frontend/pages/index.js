import { useEffect, useState } from 'react';
import { Heading, Text, SimpleGrid, Box, Flex, Button } from '@chakra-ui/react';
import { api } from '../utils/api';
import { ArtistCard, AlbumCard, SongCard } from '../components/Cards';
import Link from 'next/link';

export default function Home() {
  const [featuredArtists, setFeaturedArtists] = useState([]);
  const [newAlbums, setNewAlbums] = useState([]);
  const [topSongs, setTopSongs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        
        // Fetch data for the homepage
        const artistsResponse = await api.getArtists();
        const albumsResponse = await api.getAlbums();
        const songsResponse = await api.getSongs();
        
        // Take only a few items for featured sections
        setFeaturedArtists(artistsResponse.slice(0, 4));
        
        // Sort albums by release date (newest first)
        const sortedAlbums = [...albumsResponse].sort(
          (a, b) => new Date(b.release_date) - new Date(a.release_date)
        );
        setNewAlbums(sortedAlbums.slice(0, 4));
        
        // Sort songs by star rating (highest first)
        const sortedSongs = [...songsResponse].sort((a, b) => b.star - a.star);
        setTopSongs(sortedSongs.slice(0, 4));
        
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load data. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  if (error) {
    return (
      <Box textAlign="center" py={10}>
        <Heading mb={4}>Oh no!</Heading>
        <Text mb={6}>{error}</Text>
        <Button onClick={() => window.location.reload()}>Try Again</Button>
      </Box>
    );
  }

  return (
    <Box>
      <Box py={8} bg="blue.50" mb={8} borderRadius="lg">
        <Heading as="h1" size="2xl" textAlign="center" mb={4}>
          Welcome to Xiamiu Music
        </Heading>
        <Text fontSize="xl" textAlign="center" maxW="container.md" mx="auto">
          Discover your favorite artists, albums, and songs in one place
        </Text>
      </Box>

      {isLoading ? (
        <Flex justify="center" align="center" height="200px">
          <Text>Loading...</Text>
        </Flex>
      ) : (
        <>
          <Box mb={12}>
            <Flex justify="space-between" align="center" mb={4}>
              <Heading size="lg">Featured Artists</Heading>
              <Link href="/artists" passHref>
                <Button as="a" variant="outline" size="sm">
                  View All
                </Button>
              </Link>
            </Flex>
            <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
              {featuredArtists.map((artist) => (
                <ArtistCard key={artist.artist_id} artist={artist} />
              ))}
            </SimpleGrid>
          </Box>

          <Box mb={12}>
            <Flex justify="space-between" align="center" mb={4}>
              <Heading size="lg">New Releases</Heading>
              <Link href="/albums" passHref>
                <Button as="a" variant="outline" size="sm">
                  View All
                </Button>
              </Link>
            </Flex>
            <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
              {newAlbums.map((album) => (
                <AlbumCard key={album.album_id} album={album} />
              ))}
            </SimpleGrid>
          </Box>

          <Box mb={12}>
            <Flex justify="space-between" align="center" mb={4}>
              <Heading size="lg">Top Songs</Heading>
              <Link href="/songs" passHref>
                <Button as="a" variant="outline" size="sm">
                  View All
                </Button>
              </Link>
            </Flex>
            <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
              {topSongs.map((song) => (
                <SongCard key={song.song_id} song={song} />
              ))}
            </SimpleGrid>
          </Box>
        </>
      )}
    </Box>
  );
} 