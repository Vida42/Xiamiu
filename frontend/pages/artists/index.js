import { useEffect, useState } from 'react';
import { Heading, Text, SimpleGrid, Box, Flex, Link } from '@chakra-ui/react';
import { api } from '../../utils/api';
import { ArtistCard } from '../../components/Cards';
import XiamiuLayout from '../../components/Layout/XiamiuLayout';

export default function Artists() {
  const [artists, setArtists] = useState([]);
  const [filteredArtists, setFilteredArtists] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeFilter, setActiveFilter] = useState('all');
  
  const artistFilters = [
    { id: 'all', label: '全部' },
    { id: 'popular', label: '热门' },
    { id: 'chinese', label: '华语' },
    { id: 'western', label: '欧美' },
    { id: 'japanese', label: '日本' },
    { id: 'korean', label: '韩国' },
    { id: 'band', label: '乐队' }
  ];

  useEffect(() => {
    const fetchArtists = async () => {
      try {
        setIsLoading(true);
        const data = await api.getArtists();
        setArtists(data);
        setFilteredArtists(data);
      } catch (err) {
        console.error('Error fetching artists:', err);
        setError('Failed to load artists. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchArtists();
  }, []);

  useEffect(() => {
    if (activeFilter === 'all') {
      setFilteredArtists(artists);
      return;
    }

    // In a real application, you would filter by artist country or popularity
    // For this example, we'll just pretend to filter
    const filtered = artists.filter((_, index) => index % (artistFilters.findIndex(f => f.id === activeFilter) + 1) === 0);
    setFilteredArtists(filtered);
  }, [activeFilter, artists]);

  const renderContent = () => {
    if (error) {
      return (
        <Box textAlign="center" py={10}>
          <Heading mb={4}>Error</Heading>
          <Text>{error}</Text>
        </Box>
      );
    }

    return (
      <Box>
        <Heading size="md" mb={6}>Artists</Heading>
        
        <Flex 
          as="ul" 
          className="bottom-ul-menu"
          mb={8}
          overflowX={{ base: "auto", md: "visible" }}
        >
          {artistFilters.map(filter => (
            <Box 
              as="li" 
              key={filter.id} 
              className={activeFilter === filter.id ? "active" : ""}
            >
              <Link onClick={() => setActiveFilter(filter.id)}>
                {filter.label}
              </Link>
            </Box>
          ))}
        </Flex>

        {isLoading ? (
          <Flex justify="center" py={10}>
            <Text>Loading artists...</Text>
          </Flex>
        ) : filteredArtists.length === 0 ? (
          <Box textAlign="center" py={10}>
            <Text>No artists found in this category</Text>
          </Box>
        ) : (
          <SimpleGrid columns={{ base: 1, md: 3, lg: 5 }} spacing={3}>
            {filteredArtists.map(artist => (
              <ArtistCard key={artist.artist_id} artist={artist} />
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