import { Box, Image, Text, VStack, useColorModeValue } from '@chakra-ui/react';
import NextLink from 'next/link';
import { useState, useEffect } from 'react';
import { api } from '../../utils/api';

const AlbumCard = ({ album }) => {
  const [albumMeta, setAlbumMeta] = useState(null);
  const bgColor = useColorModeValue('white', 'gray.800');
  const hoverBg = useColorModeValue('gray.50', 'gray.700');
  
  useEffect(() => {
    const fetchAlbumMeta = async () => {
      try {
        const meta = await api.getAlbumMeta(album.album_id);
        setAlbumMeta(meta);
      } catch (error) {
        console.error(`Error fetching album metadata for ${album.album_id}:`, error);
      }
    };
    
    if (album && album.album_id) {
      fetchAlbumMeta();
    }
  }, [album]);

  // Format date to match Xiamiu style (YYYY-MM-DD)
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', { 
      year: 'numeric', 
      month: '2-digit', 
      day: '2-digit' 
    }).replace(/\//g, '-');
  };

  return (
    <Box
      as={NextLink}
      href={`/albums/${album.album_id}`}
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
          src={albumMeta?.pic_address || '/album-placeholder.svg'}
          alt={album.name}
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
          {album.name}
        </Text>
        <Text 
          fontSize="xs" 
          color="gray.500" 
          noOfLines={1}
          fontFamily="'Microsoft YaHei', 'STHeiti', sans-serif"
        >
          {album.artist?.name}
        </Text>
        {album.release_date && (
          <Text 
            fontSize="xs" 
            color="gray.400"
            fontFamily="'Microsoft YaHei', 'STHeiti', sans-serif"
          >
            {formatDate(album.release_date)}
          </Text>
        )}
      </VStack>
    </Box>
  );
};

export default AlbumCard; 