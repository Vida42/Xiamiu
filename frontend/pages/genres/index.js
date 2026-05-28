import { useEffect, useState } from 'react';
import { Heading, Text, SimpleGrid, Box, Flex, Link } from '@chakra-ui/react';
import { api } from '../../utils/api';
import { GenreCard } from '../../components/Cards';
import XiamiuLayout from '../../components/Layout/XiamiuLayout';
import { useLanguage } from '../../contexts/LanguageContext';

export default function Genres() {
  const { t } = useLanguage();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [genres, setGenres] = useState([]);


  useEffect(() => {
    const fetchGenres = async () => {
      try {
        setIsLoading(true);
        const data = await api.getGenres();
        setGenres(data);
      } catch (err) {
        console.error('Error fetching genres:', err);
        setError(t('failedLoadGenres'));
      } finally {
        setIsLoading(false);
      }
    };

    fetchGenres();
  }, []);

  const renderContent = () => {
    if (error) {
      return (
        <Box textAlign="center" py={10}>
          <Heading mb={4}>{t('error')}</Heading>
          <Text>{error}</Text>
        </Box>
      );
    }

    return (
      <Box>
        <Heading size="md" mb={6}>{t('genres')}</Heading>
        {isLoading ? (
          <Flex justify="center" py={10}>
            <Text>{t('loadingGenres')}</Text>
          </Flex>
        ) : (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
            {genres.map(genre => (
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
