import { Box, Image, Text, VStack, HStack, useColorModeValue } from '@chakra-ui/react';
import NextLink from 'next/link';
import { useEffect, useState } from 'react';
import { api } from '../../utils/api';

const SongCard = ({ song }) => {
  const [albumInfo, setAlbumInfo] = useState(null);
  const bgColor = useColorModeValue('white', 'gray.800');
  const hoverBg = useColorModeValue('gray.50', 'gray.700');

  useEffect(() => {
    // Fetch album info to get the cover image
    const fetchAlbumInfo = async () => {
      if (song.album_id) {
        try {
          const albumData = await api.getAlbumMeta(song.album_id);
          setAlbumInfo(albumData);
        } catch (error) {
          console.error('Error fetching album info:', error);
        }
      }
    };

    fetchAlbumInfo();
  }, [song.album_id]);

  return (
    <Box
      as={NextLink}
      href={`/songs/${song.song_id}`}
      bg={bgColor}
      p={3}
      rounded="md"
      shadow="sm"
      transition="all 0.2s"
      _hover={{
        transform: 'translateY(-3px)',
        shadow: 'md',
        bg: hoverBg,
        textDecoration: 'none',
      }}
      display="block"
      height="100%"
    >
      <Box position="relative" mb={3} overflow="hidden" borderRadius="md">
        <Image
          src={albumInfo?.pic_address || '/album-placeholder.svg'}
          alt={song.name}
          w="100%"
          h="180px"
          objectFit="cover"
          fallbackSrc="/album-placeholder.svg"
        />
        <Box
          position="absolute"
          top={0}
          left={0}
          right={0}
          bottom={0}
          bg="blackAlpha.200"
          opacity={0}
          transition="opacity 0.2s"
          _groupHover={{ opacity: 1 }}
          cursor="pointer"
        />
      </Box>
      <VStack align="start" spacing={1}>
        <Text 
          fontWeight="bold" 
          noOfLines={1}
          fontSize="sm"
          fontFamily="'Microsoft YaHei', 'STHeiti', sans-serif"
        >
          {song.name}
        </Text>
        <HStack spacing={1}>
          {song.star && (
            <HStack spacing={0}>
              {Array.from({ length: parseInt(song.star) }).map((_, i) => (
                <Text key={i} color="xiamiOrange" fontSize="xs">★</Text>
              ))}
            </HStack>
          )}
        </HStack>
        {song.artist && (
          <Text 
            fontSize="xs" 
            color="gray.500" 
            noOfLines={1}
            fontFamily="'Microsoft YaHei', 'STHeiti', sans-serif"
          >
            {song.artist.name}
          </Text>
        )}
      </VStack>
    </Box>
  );
};

export default SongCard; 