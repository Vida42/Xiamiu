import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import NextLink from 'next/link';
import { Box, Heading, Text, Image, SimpleGrid, Tabs, TabList, Tab, TabPanels, TabPanel, Flex, Badge, Link, Divider, HStack, Icon, Table, Thead, Tbody, Tr, Td, VStack } from '@chakra-ui/react';
import { api } from '../../utils/api';
import { SongCard } from '../../components/Cards';
import XiamiuLayout from '../../components/Layout/XiamiuLayout';

export default function AlbumDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [album, setAlbum] = useState(null);
  const [albumMeta, setAlbumMeta] = useState(null);
  const [songs, setSongs] = useState([]);
  const [artist, setArtist] = useState(null);
  const [comments, setComments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAlbumData = async () => {
      if (!id) return;
      
      try {
        setIsLoading(true);
        
        // Fetch album details
        const albumData = await api.getAlbum(id);
        setAlbum(albumData);
        
        // Fetch artist details
        try {
          const artistData = await api.getArtist(albumData.artist_id);
          setArtist(artistData);
        } catch (artistErr) {
          console.log('Failed to load artist details');
        }
        
        // Fetch album's songs
        const songsData = await api.getAlbumSongs(id);
        setSongs(songsData);
        
        // Try to fetch album metadata
        try {
          const metaData = await api.getAlbumMeta(id);
          setAlbumMeta(metaData);
        } catch (metaErr) {
          console.log('No metadata available for this album');
        }
        
        // Try to fetch album comments
        try {
          const commentsData = await api.getAlbumComments(id);
          setComments(commentsData);
        } catch (commentsErr) {
          console.log('No comments available for this album');
        }
        
      } catch (err) {
        console.error('Error fetching album data:', err);
        setError('Failed to load album details. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchAlbumData();
  }, [id]);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  const renderContent = () => {
    if (!id) return null;

    if (error) {
      return (
        <Box textAlign="center" py={10}>
          <Heading mb={4}>Error</Heading>
          <Text>{error}</Text>
        </Box>
      );
    }

    if (isLoading) {
      return (
        <Box textAlign="center" py={10}>
          <Text>Loading album details...</Text>
        </Box>
      );
    }

    if (!album) {
      return (
        <Box textAlign="center" py={10}>
          <Heading mb={4}>Album Not Found</Heading>
          <Text>The album you're looking for doesn't exist.</Text>
          <NextLink href="/albums" passHref legacyBehavior>
            <Link color="blue.500" mt={4} display="inline-block">
              Back to Albums
            </Link>
          </NextLink>
        </Box>
      );
    }

    return (
      <Box>
        <Box mb={8}>
          <Flex direction={{ base: 'column', md: 'row' }} gap={8}>
            <Box flexShrink={0} maxW={{ base: '100%', md: '300px' }}>
              <Image
                src={albumMeta?.pic_address || '/album-placeholder.svg'}
                alt={album.name}
                borderRadius="lg"
                width="100%"
                height="auto"
                objectFit="cover"
                crossOrigin="anonymous"
                fallbackSrc="/album-placeholder.svg"
              />
              <Flex justify="center" mt={2}>
                {Array.from({ length: album.star }).map((_, i) => (
                  <Text key={i} fontSize="xl">⭐</Text>
                ))}
              </Flex>
            </Box>
            
            <Box>
              <Heading size="2xl" mb={4}>{album.name}</Heading>
              
              {artist && (
                <Flex gap={2} mb={4}>
                  <Text fontWeight="bold">Artist:</Text>
                  <NextLink href={`/artists/${artist.artist_id}`} passHref legacyBehavior>
                    <Link fontSize="md" color="blue.500">
                      {artist.name}
                    </Link>
                  </NextLink>
                </Flex>
              )}
              
              <Box mt={4}>
                <VStack spacing={2} align="flex-start">
                  <Flex>
                    <Text fontWeight="bold" width="120px">Release Date:</Text>
                    <Text>{formatDate(album.release_date)}</Text>
                  </Flex>
                  
                  <Flex>
                    <Text fontWeight="bold" width="120px">Language:</Text>
                    <Text>{album.album_lan}</Text>
                  </Flex>
                  
                  <Flex>
                    <Text fontWeight="bold" width="120px">Category:</Text>
                    <Text>{album.album_category}</Text>
                  </Flex>
                  
                  {album.record_label && album.record_label !== "''" && (
                    <Flex>
                      <Text fontWeight="bold" width="120px">Record Label:</Text>
                      <Text>{album.record_label}</Text>
                    </Flex>
                  )}
                </VStack>
              </Box>
              
              {albumMeta && albumMeta.info && (
                <Box mt={6} mb={4}>
                  <Heading as="h3" size="md" mb={3}>Description</Heading>
                  <Text fontSize="md" lineHeight="1.7" px={3} py={4} bg="gray.50" borderRadius="md">
                    {albumMeta.info}
                  </Text>
                </Box>
              )}
              
              <Divider my={4} />
              
              <NextLink href="/albums" passHref legacyBehavior>
                <Link color="blue.500">
                  Back to All Albums
                </Link>
              </NextLink>
            </Box>
          </Flex>
        </Box>
        
        <Tabs isLazy colorScheme="blue" mt={8}>
          <TabList>
            <Tab>Songs ({songs.length})</Tab>
            <Tab>Comments ({comments.length})</Tab>
          </TabList>
          
          <TabPanels>
            <TabPanel>
              {songs.length === 0 ? (
                <Text py={4}>No songs available for this album.</Text>
              ) : (
                <Box mt={4} borderWidth="1px" borderRadius="lg" overflow="hidden">
                  <Table variant="simple">
                    <Tbody>
                      {songs.map((song, index) => (
                        <Tr key={song.song_id} _hover={{ bg: "gray.50" }}>
                          <Td width="50px" color="gray.500">{index + 1}</Td>
                          <Td>
                            <NextLink href={`/songs/${song.song_id}`} passHref legacyBehavior>
                              <Link fontWeight="medium" color="blue.600">
                                {song.name}
                              </Link>
                            </NextLink>
                          </Td>
                          <Td isNumeric>
                            <Badge colorScheme="yellow">
                              {Array.from({ length: song.star }).map((_, i) => (
                                <span key={i}>⭐</span>
                              ))}
                            </Badge>
                          </Td>
                        </Tr>
                      ))}
                    </Tbody>
                  </Table>
                </Box>
              )}
            </TabPanel>
            
            <TabPanel>
              {comments.length === 0 ? (
                <Text py={4}>No comments available for this album.</Text>
              ) : (
                <Box mt={4}>
                  {comments.map(comment => (
                    <Box 
                      key={comment.id} 
                      p={4} 
                      borderWidth="1px" 
                      borderRadius="md"
                      mb={4}
                    >
                      <Text>{comment.comment}</Text>
                      <Flex mt={2} justify="space-between" alignItems="center">
                        <Text fontSize="sm" color="gray.500">
                          Posted on {new Date(comment.review_date).toLocaleDateString()}
                        </Text>
                        <Badge colorScheme="green">
                          {comment.num_like} likes
                        </Badge>
                      </Flex>
                    </Box>
                  ))}
                </Box>
              )}
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