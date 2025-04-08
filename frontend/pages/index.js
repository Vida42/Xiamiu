import { useEffect, useState } from 'react';
import { Heading, Text, SimpleGrid, Box, Flex, Button, Link, Image, VStack, HStack, useColorModeValue } from '@chakra-ui/react';
import { api } from '../utils/api';
import { ArtistCard, GenreCard } from '../components/Cards';
import { AlbumCard, SongCard } from '../components/Cards/index';
import NextLink from 'next/link';
import XiamiuLayout from '../components/Layout/XiamiuLayout';
import PlaylistSection from '../components/PlaylistSection';

const SectionHeader = ({ title, showMore = true }) => {
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
        {showMore && (
          <NextLink href="#" passHref>
            <Link 
              ml={2} 
              color="#f60" 
              fontFamily="'Microsoft YaHei', 'STHeiti', sans-serif"
              fontSize="14px"
            >
              / 更多
            </Link>
          </NextLink>
        )}
      </Flex>
    </Flex>
  );
};

const LanguageFilter = ({ languages, selectedLang, onSelect }) => {
  const buttonBg = useColorModeValue('gray.100', 'gray.700');
  const activeBg = useColorModeValue('orange.500', 'orange.600');
  
  return (
    <HStack spacing={4} mb={4} fontFamily="'Microsoft YaHei', 'STHeiti', sans-serif">
      {languages.map(lang => (
        <Box
          key={lang.value}
          px={3}
          py={1}
          rounded="full"
          cursor="pointer"
          bg={selectedLang === lang.value ? activeBg : buttonBg}
          color={selectedLang === lang.value ? 'white' : 'inherit'}
          onClick={() => onSelect(lang.value)}
          fontWeight={selectedLang === lang.value ? 'bold' : 'normal'}
          fontSize="sm"
        >
          {lang.label}
        </Box>
      ))}
    </HStack>
  );
};

export default function Home() {
  const [featuredArtists, setFeaturedArtists] = useState([]);
  const [newAlbums, setNewAlbums] = useState([]);
  const [topSongs, setTopSongs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [recommendedSongs, setRecommendedSongs] = useState([]);
  const [selectedLang, setSelectedLang] = useState('all');
  const [filteredAlbums, setFilteredAlbums] = useState([]);
  
  const languages = [
    { label: '全部', value: 'all' },
    { label: '华语', value: 'chinese' },
    { label: '欧美', value: 'western' },
    { label: '日本', value: 'japanese' },
    { label: '韩国', value: 'korean' }
  ];

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
        setNewAlbums(sortedAlbums.slice(0, 8));
        setFilteredAlbums(sortedAlbums.slice(0, 8));
        
        // Sort songs by star rating (highest first)
        const sortedSongs = [...songsResponse].sort((a, b) => b.star - a.star);
        setTopSongs(sortedSongs.slice(0, 4));
        
        // Use the getSongs method instead of direct get call
        const recommendedSongs = await api.getSongs();
        // Just take the first 5 songs as recommendations (in a real app, you'd have a dedicated endpoint)
        setRecommendedSongs(recommendedSongs.slice(0, 5));
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load data. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  // Filter albums based on selected language
  useEffect(() => {
    if (selectedLang === 'all') {
      setFilteredAlbums(newAlbums);
    } else {
      // This is a simplified example - in a real app you'd have language info in the album data
      // For now, we'll just filter randomly to demonstrate the functionality
      const filtered = newAlbums.filter((_, index) => {
        // For demo purposes: assign each album to a language group based on its index
        const languages = ['chinese', 'western', 'japanese', 'korean'];
        const albumLang = languages[index % languages.length];
        return albumLang === selectedLang;
      });
      setFilteredAlbums(filtered.length ? filtered : [newAlbums[0]]); // Ensure at least one result
    }
  }, [selectedLang, newAlbums]);

  if (error) {
    return (
      <XiamiuLayout>
        <Box textAlign="center" py={10}>
          <Heading mb={4}>Oh no!</Heading>
          <Text mb={6}>{error}</Text>
          <Button onClick={() => window.location.reload()}>Try Again</Button>
        </Box>
      </XiamiuLayout>
    );
  }

  return (
    <XiamiuLayout>
      {isLoading ? (
        <Flex justify="center" align="center" height="200px">
          <Text>Loading...</Text>
        </Flex>
      ) : (
        <>
          {/* Recommended Songs Section */}
          <Box mb={12}>
            <SectionHeader title="猜你喜欢" />
            <SimpleGrid columns={{ base: 1, sm: 2, md: 3, lg: 5 }} spacing={3}>
              {recommendedSongs.map(song => (
                <SongCard key={song.song_id} song={song} />
              ))}
            </SimpleGrid>
          </Box>

          {/* New Albums Section */}
          <Box mb={12}>
            <SectionHeader title="新碟首发" />
            <LanguageFilter
              languages={languages}
              selectedLang={selectedLang}
              onSelect={setSelectedLang}
            />
            <SimpleGrid columns={{ base: 1, sm: 2, md: 3, lg: 5 }} spacing={3}>
              {filteredAlbums.map(album => (
                <AlbumCard key={album.album_id} album={album} />
              ))}
            </SimpleGrid>
          </Box>

          {/* Playlist Section */}
          <PlaylistSection />
        </>
      )}
    </XiamiuLayout>
  );
} 