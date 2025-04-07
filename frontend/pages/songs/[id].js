import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import NextLink from 'next/link';
import { Box, Heading, Text, SimpleGrid, Tabs, TabList, Tab, TabPanels, TabPanel, Flex, Badge, Link, Divider, HStack, VStack } from '@chakra-ui/react';
import { api } from '../../utils/api';
import XiamiuLayout from '../../components/Layout/XiamiuLayout';

export default function SongDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [song, setSong] = useState(null);
  const [songMeta, setSongMeta] = useState(null);
  const [album, setAlbum] = useState(null);
  const [artists, setArtists] = useState([]);
  const [comments, setComments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSongData = async () => {
      if (!id) return;
      
      try {
        setIsLoading(true);
        
        // Fetch song details
        const songData = await api.getSong(id);
        setSong(songData);
        
        // Fetch album details
        try {
          const albumData = await api.getAlbum(songData.album_id);
          setAlbum(albumData);
          
          // TODO: In a real app, fetch artists associated with the song
          // This would be a separate API endpoint in the backend
          // For now, we'll just use a placeholder
          setArtists([{ artist_id: 'ART001', name: 'Artist Name' }]);
        } catch (albumErr) {
          console.log('Failed to load album details');
        }
        
        // Try to fetch song metadata (lyrics)
        try {
          const metaData = await api.getSongMeta(id);
          setSongMeta(metaData);
        } catch (metaErr) {
          console.log('No metadata available for this song');
        }
        
        // Try to fetch song comments
        try {
          const commentsData = await api.getSongComments(id);
          setComments(commentsData);
        } catch (commentsErr) {
          console.log('No comments available for this song');
        }
        
      } catch (err) {
        console.error('Error fetching song data:', err);
        setError('Failed to load song details. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSongData();
  }, [id]);

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
          <Text>Loading song details...</Text>
        </Box>
      );
    }

    if (!song) {
      return (
        <Box textAlign="center" py={10}>
          <Heading mb={4}>Song Not Found</Heading>
          <Text>The song you're looking for doesn't exist.</Text>
          <NextLink href="/songs" passHref legacyBehavior>
            <Link color="blue.500" mt={4} display="inline-block">
              Back to Songs
            </Link>
          </NextLink>
        </Box>
      );
    }

    return (
      <Box>
        <VStack align="start" spacing={6} mb={8}>
          <Box width="100%">
            <Heading size="2xl" mb={2}>{song.name}</Heading>
            
            <Flex flexWrap="wrap" align="center" gap={2} mb={4}>
              {artists.map(artist => (
                <NextLink key={artist.artist_id} href={`/artists/${artist.artist_id}`} passHref legacyBehavior>
                  <Link color="blue.500" fontSize="lg">
                    {artist.name}
                  </Link>
                </NextLink>
              ))}
              
              {album && (
                <>
                  <Text mx={2}>•</Text>
                  <NextLink href={`/albums/${album.album_id}`} passHref legacyBehavior>
                    <Link color="purple.500" fontSize="lg">
                      {album.name}
                    </Link>
                  </NextLink>
                </>
              )}
            </Flex>
            
            <Flex mb={6}>
              {Array.from({ length: song.star }).map((_, i) => (
                <Text key={i} fontSize="xl">⭐</Text>
              ))}
            </Flex>
          </Box>
          
          <Box width="100%" borderWidth="1px" borderRadius="lg" p={6} bg="gray.50">
            <Heading size="md" mb={4}>Song Information</Heading>
            <Flex justify="space-between" flexWrap="wrap" gap={4}>
              <Box>
                <Text fontWeight="bold">Song ID</Text>
                <Text>{song.song_id}</Text>
              </Box>
              
              {album && (
                <>
                  <Box>
                    <Text fontWeight="bold">Album</Text>
                    <NextLink href={`/albums/${album.album_id}`} passHref legacyBehavior>
                      <Link color="blue.500">{album.name}</Link>
                    </NextLink>
                  </Box>
                  
                  <Box>
                    <Text fontWeight="bold">Release Date</Text>
                    <Text>{new Date(album.release_date).toLocaleDateString()}</Text>
                  </Box>
                </>
              )}
              
              <Box>
                <Text fontWeight="bold">Rating</Text>
                <Text>{song.star} / 5</Text>
              </Box>
            </Flex>
          </Box>
            
          <Divider />
          
          <NextLink href="/songs" passHref legacyBehavior>
            <Link color="blue.500">
              Back to All Songs
            </Link>
          </NextLink>
        </VStack>
        
        <Tabs isLazy colorScheme="blue" mt={8}>
          <TabList>
            <Tab>Lyrics</Tab>
            <Tab>Comments ({comments.length})</Tab>
          </TabList>
          
          <TabPanels>
            <TabPanel>
              {songMeta ? (
                <Box 
                  whiteSpace="pre-wrap" 
                  p={6} 
                  bg="gray.50" 
                  borderRadius="md"
                  fontFamily="body"
                  lineHeight="tall"
                >
                  {songMeta.lyrics}
                </Box>
              ) : (
                <Text py={4}>No lyrics available for this song.</Text>
              )}
            </TabPanel>
            
            <TabPanel>
              {comments.length === 0 ? (
                <Text py={4}>No comments available for this song.</Text>
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