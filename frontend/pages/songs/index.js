import { useEffect, useState } from 'react';
import { Heading, Text, SimpleGrid, Box, Flex, Input, InputGroup, InputLeftElement, Select } from '@chakra-ui/react';
import { api } from '../../utils/api';
import { SongCard } from '../../components/Cards';

export default function Songs() {
  const [songs, setSongs] = useState([]);
  const [filteredSongs, setFilteredSongs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('name');

  useEffect(() => {
    const fetchSongs = async () => {
      try {
        setIsLoading(true);
        const data = await api.getSongs();
        setSongs(data);
        setFilteredSongs(data);
      } catch (err) {
        console.error('Error fetching songs:', err);
        setError('Failed to load songs. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSongs();
  }, []);

  useEffect(() => {
    let result = [...songs];
    
    // Filter by search term
    if (searchTerm.trim()) {
      result = result.filter(song => 
        song.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // Sort results
    switch (sortBy) {
      case 'name':
        result.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'rating_high':
        result.sort((a, b) => b.star - a.star);
        break;
      case 'rating_low':
        result.sort((a, b) => a.star - b.star);
        break;
      default:
        break;
    }
    
    setFilteredSongs(result);
  }, [searchTerm, sortBy, songs]);

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
      <Heading mb={6}>Songs</Heading>
      
      <Flex 
        direction={{ base: 'column', md: 'row' }} 
        gap={4} 
        mb={8} 
        justifyContent="space-between"
        alignItems={{ base: 'stretch', md: 'center' }}
      >
        <InputGroup maxW={{ base: '100%', md: '500px' }}>
          <InputLeftElement pointerEvents="none">🔍</InputLeftElement>
          <Input 
            placeholder="Filter songs by name..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </InputGroup>
        
        <Select 
          value={sortBy} 
          onChange={(e) => setSortBy(e.target.value)}
          maxW={{ base: '100%', md: '200px' }}
        >
          <option value="name">Name (A-Z)</option>
          <option value="rating_high">Highest Rated</option>
          <option value="rating_low">Lowest Rated</option>
        </Select>
      </Flex>

      {isLoading ? (
        <Flex justify="center" py={10}>
          <Text>Loading songs...</Text>
        </Flex>
      ) : filteredSongs.length === 0 ? (
        <Box textAlign="center" py={10}>
          <Text>No songs found matching "{searchTerm}"</Text>
        </Box>
      ) : (
        <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
          {filteredSongs.map(song => (
            <SongCard key={song.song_id} song={song} />
          ))}
        </SimpleGrid>
      )}
    </Box>
  );
} 