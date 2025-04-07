import { useEffect, useState } from 'react';
import { Heading, Text, SimpleGrid, Box, Flex, Input, InputGroup, InputLeftElement } from '@chakra-ui/react';
import { api } from '../../utils/api';
import { ArtistCard } from '../../components/Cards';
import XiamiuLayout from '../../components/Layout/XiamiuLayout';
import { SearchIcon } from '@chakra-ui/icons';

export default function Artists() {
  const [artists, setArtists] = useState([]);
  const [filteredArtists, setFilteredArtists] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

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
    if (!searchTerm.trim()) {
      setFilteredArtists(artists);
      return;
    }

    const filtered = artists.filter(artist => 
      artist.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredArtists(filtered);
  }, [searchTerm, artists]);

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
        <Heading mb={6}>Artists</Heading>
        
        <InputGroup mb={8} maxW="500px">
          <InputLeftElement pointerEvents="none">
            <SearchIcon color="gray.300" />
          </InputLeftElement>
          <Input 
            placeholder="Filter artists by name..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </InputGroup>

        {isLoading ? (
          <Flex justify="center" py={10}>
            <Text>Loading artists...</Text>
          </Flex>
        ) : filteredArtists.length === 0 ? (
          <Box textAlign="center" py={10}>
            <Text>No artists found matching "{searchTerm}"</Text>
          </Box>
        ) : (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
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