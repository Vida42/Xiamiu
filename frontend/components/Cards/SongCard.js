import { Box, Image, Heading, Text, Badge, Stack, LinkBox, LinkOverlay, Flex, VStack } from '@chakra-ui/react';
import NextLink from 'next/link';
import { useEffect, useState } from 'react';
import { api } from '../../utils/api';

const SongCard = ({ song }) => {
  const [album, setAlbum] = useState(null);
  const [albumMeta, setAlbumMeta] = useState(null);
  
  useEffect(() => {
    const fetchAlbumData = async () => {
      if (song && song.album_id) {
        try {
          // Fetch album details
          const albumData = await api.getAlbum(song.album_id);
          setAlbum(albumData);
          
          // Try to fetch album cover
          try {
            const albumMetaData = await api.getAlbumMeta(song.album_id);
            setAlbumMeta(albumMetaData);
          } catch (metaErr) {
            console.log('No album meta available');
          }
        } catch (error) {
          console.error(`Error fetching album data for song ${song.song_id}:`, error);
        }
      }
    };
    
    fetchAlbumData();
  }, [song]);

  return (
    <LinkBox
      as="article"
      bg="white"
      p={3}
      rounded="md"
      shadow="sm"
      transition="all 0.2s"
      _hover={{
        transform: 'translateY(-3px)',
        shadow: 'md',
        bg: 'gray.50',
        textDecoration: 'none',
      }}
      display="block"
      height="100%"
    >
      <Box position="relative" mb={3} overflow="hidden" borderRadius="md">
        <Image
          src={albumMeta?.pic_address || '/album-placeholder.svg'}
          alt={song.name}
          w="100%"
          h="120px"
          objectFit="cover"
          fallbackSrc="/album-placeholder.svg"
        />
      </Box>
      
      <VStack align="start" spacing={1}>
        <NextLink href={`/songs/${song.song_id}`} passHref legacyBehavior>
          <LinkOverlay>
            <Text 
              fontWeight="bold" 
              noOfLines={1} 
              fontSize="sm"
              fontFamily="'Microsoft YaHei', 'STHeiti', sans-serif"
            >
              {song.name}
            </Text>
          </LinkOverlay>
        </NextLink>
        
        {album && (
          <NextLink href={`/albums/${album.album_id}`} passHref>
            <Text 
              fontSize="xs" 
              color="gray.500" 
              noOfLines={1}
              fontFamily="'Microsoft YaHei', 'STHeiti', sans-serif"
              cursor="pointer"
              _hover={{ color: "orange.500" }}
            >
              {album.name}
            </Text>
          </NextLink>
        )}
        
        <Flex justifyContent="flex-end" width="100%">
          <Badge colorScheme="yellow" fontSize="10px" px={1}>
            {Array.from({ length: song.star }).map((_, i) => (
              <Text as="span" key={i} fontSize="10px" lineHeight="1">⭐</Text>
            ))}
          </Badge>
        </Flex>
      </VStack>
    </LinkBox>
  );
};

export default SongCard; 