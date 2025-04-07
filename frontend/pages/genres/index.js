import { useEffect, useState } from 'react';
import { Heading, Text, SimpleGrid, Box, Flex, Input, InputGroup, InputLeftElement } from '@chakra-ui/react';
import { api } from '../../utils/api';
import { GenreCard } from '../../components/Cards';
import XiamiuLayout from '../../components/Layout/XiamiuLayout';
import { SearchIcon } from '@chakra-ui/icons';

export default function Genres() {
  const [genres, setGenres] = useState([]);
  const [filteredGenres, setFilteredGenres] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchGenres = async () => {
      try {
        setIsLoading(true);
        const data = await api.getGenres();
        setGenres(data);
        setFilteredGenres(data);
      } catch (err) {
        console.error('Error fetching genres:', err);
        setError('Failed to load genres. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchGenres();
  }, []);

  useEffect(() => {
    if (!searchTerm.trim()) {
      setFilteredGenres(genres);
      return;
    }

    const filtered = genres.filter(genre => 
      genre.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredGenres(filtered);
  }, [searchTerm, genres]);

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
        <Heading mb={6}>Genres</Heading>
        
        <InputGroup mb={8} maxW="500px">
          <InputLeftElement pointerEvents="none">
            <SearchIcon color="gray.300" />
          </InputLeftElement>
          <Input 
            placeholder="Filter genres by name..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </InputGroup>

        {isLoading ? (
          <Flex justify="center" py={10}>
            <Text>Loading genres...</Text>
          </Flex>
        ) : filteredGenres.length === 0 ? (
          <Box textAlign="center" py={10}>
            <Text>No genres found matching "{searchTerm}"</Text>
          </Box>
        ) : (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
            {filteredGenres.map(genre => (
              <GenreCard key={genre.id} genre={genre} />
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