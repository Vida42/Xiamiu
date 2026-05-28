import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import NextLink from 'next/link';
import { Box, Heading, Text, Image, SimpleGrid, Flex, Link, Table, Thead, Tbody, Tr, Th, Td, Badge } from '@chakra-ui/react';
import { api } from '../../../../utils/api';
import XiamiuLayout from '../../../../components/Layout/XiamiuLayout';
import { useLanguage } from '../../../../contexts/LanguageContext';

const SectionHeader = ({ title, showMore = false }) => {
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

const formatDuration = (seconds) => {
  if (!seconds) return '0:00';
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
};

export default function ArtistCollection() {
  const router = useRouter();
  const { id, rating } = router.query;
  const [artist, setArtist] = useState(null);
  const [songs, setSongs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const { t } = useLanguage();

  useEffect(() => {
    const fetchCollectionData = async () => {
      if (!id || !rating) return;
      
      try {
        setIsLoading(true);
        
        // Fetch artist details
        const artistData = await api.getArtist(id);
        setArtist(artistData);
        
        // Fetch artist's albums
        const albumsData = await api.getArtistAlbums(id);
        
        // Fetch all songs from all albums
        const allSongs = [];
        for (const album of albumsData) {
          const albumSongs = await api.getAlbumSongs(album.album_id);
          // Enhance songs with album info
          const songsWithAlbumInfo = albumSongs.map(song => ({
            ...song,
            albumName: album.name,
            albumId: album.album_id,
            release_date: album.release_date
          }));
          allSongs.push(...songsWithAlbumInfo);
        }
        
        // Filter songs by star rating
        const filteredSongs = allSongs.filter(song => song.star === parseInt(rating));
        setSongs(filteredSongs);
        
      } catch (err) {
        console.error('Error fetching collection data:', err);
        setError(t('failedLoadCollection'));
      } finally {
        setIsLoading(false);
      }
    };

    fetchCollectionData();
  }, [id, rating]);

  const renderContent = () => {
    if (!id || !rating) return null;

    if (error) {
      return (
        <Box textAlign="center" py={10}>
          <Heading mb={4}>{t('error')}</Heading>
          <Text>{error}</Text>
        </Box>
      );
    }

    if (isLoading) {
      return (
        <Box textAlign="center" py={10}>
          <Text>{t('loading')}</Text>
        </Box>
      );
    }

    const stars = parseInt(rating);
    const starDisplay = Array.from({ length: stars }).map((_, i) => '⭐').join('');
    const artistName = artist?.name || t('unknownArtist');
    const collectionTitle = `${artistName} - ${t('starCollection', { stars })}`;

    return (
      <Box>
        <Flex direction={{ base: 'column', md: 'row' }} mb={8} gap={6}>
          <Box maxW={{ base: '100%', md: '250px' }} flexShrink={0}>
            <Box position="relative" borderRadius="md" overflow="hidden">
              <Image
                src="/album-placeholder.svg"
                alt={collectionTitle}
                w="100%"
                borderRadius="md"
              />
              <Flex 
                position="absolute" 
                bottom="0" 
                left="0" 
                right="0" 
                bg="rgba(0,0,0,0.6)" 
                color="white"
                p={3}
                justifyContent="center"
                alignItems="center"
              >
                {Array.from({ length: stars }).map((_, i) => (
                  <Text as="span" key={i} fontSize="18px" lineHeight="1" mr="2px">⭐</Text>
                ))}
              </Flex>
            </Box>
          </Box>
          
          <Box>
            <Heading size="lg" mb={3} fontFamily="'Microsoft YaHei', 'STHeiti', sans-serif">
              {t('starCollection', { stars })}
            </Heading>
            <Text fontSize="md" mb={2} fontFamily="'Microsoft YaHei', 'STHeiti', sans-serif">
              {t('artist')}: {artistName}
            </Text>
            <Text fontSize="md" mb={4} color="gray.600" fontFamily="'Microsoft YaHei', 'STHeiti', sans-serif">
              {t('songCount', { count: songs.length })}
            </Text>
            <Text fontSize="md" fontFamily="'Microsoft YaHei', 'STHeiti', sans-serif">
              {t('collectionDescription', { stars, artist: artistName })}
            </Text>
          </Box>
        </Flex>
        
        <Box mt={8}>
          <SectionHeader title={t('songList')} />
          
          {songs.length === 0 ? (
            <Text py={4}>{t('noSongsInCollection')}</Text>
          ) : (
            <Box mt={4}>
              <Table variant="simple" size="md">
                <Thead>
                  <Tr borderBottom="1px solid" borderColor="gray.200">
                    <Th width="60px" textAlign="center" fontWeight="normal" fontSize="sm" color="gray.500" py={3}>#</Th>
                    <Th fontWeight="normal" fontSize="sm" color="gray.500" py={3}>{t('song')}</Th>
                    <Th fontWeight="normal" fontSize="sm" color="gray.500" py={3}>{t('album')}</Th>
                    <Th width="120px" fontWeight="normal" fontSize="sm" color="gray.500" py={3}>{t('rating')}</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {songs.map((song, index) => (
                    <Tr key={song.song_id} borderBottom="1px solid" borderColor="gray.100">
                      <Td textAlign="center" color="gray.500" fontSize="sm" py={3}>{index + 1}</Td>
                      <Td py={3}>
                        <NextLink href={`/songs/${song.song_id}`} passHref>
                          <Link 
                            color="black" 
                            _hover={{ textDecoration: 'underline' }}
                            fontSize="sm"
                          >
                            {song.name}
                          </Link>
                        </NextLink>
                      </Td>
                      <Td py={3}>
                        <NextLink href={`/albums/${song.albumId}`} passHref>
                          <Link 
                            color="gray.600" 
                            fontSize="sm"
                            _hover={{ textDecoration: 'underline' }}
                          >
                            {song.albumName}
                          </Link>
                        </NextLink>
                      </Td>
                      <Td py={3}>
                        {Array.from({ length: song.star }).map((_, i) => (
                          <Text as="span" key={i} fontSize="xs">⭐</Text>
                        ))}
                      </Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            </Box>
          )}
        </Box>
        
        <Box mt={8} mb={4}>
          <NextLink href={`/artists/${id}`} passHref>
            <Link color="#f60" fontFamily="'Microsoft YaHei', 'STHeiti', sans-serif">
              &larr; {t('backToArtistPage')}
            </Link>
          </NextLink>
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
