import { Box, Image, Text, LinkBox, LinkOverlay, Flex } from '@chakra-ui/react';
import NextLink from 'next/link';
import { StarRating } from '../../components';

const CollectionCard = ({ artistId, starRating, songCount }) => {
  // Format the collection title based on star rating
  const formatTitle = (stars) => {
    return `${stars} Star Collection`;
  };

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
        <NextLink 
          href={`/artists/${artistId}/collections/${starRating}`} 
          passHref 
          legacyBehavior
        >
          <LinkOverlay>
            <Image
              src="/album-placeholder.svg"
              alt={`${starRating} Star Collection`}
              w="100%"
              h="140px"
              objectFit="cover"
            />
            <Flex 
              position="absolute" 
              bottom="0" 
              left="0" 
              right="0" 
              bg="rgba(0,0,0,0.6)" 
              color="white"
              p={2}
              justifyContent="center"
              alignItems="center"
            >
              <StarRating rating={starRating} maxStars={5} size="md" />
            </Flex>
          </LinkOverlay>
        </NextLink>
      </Box>
      
      <Box>
        <Text 
          fontWeight="bold" 
          fontSize="sm"
          textAlign="center"
          fontFamily="'Microsoft YaHei', 'STHeiti', sans-serif"
        >
          {formatTitle(starRating)}
        </Text>
        {songCount > 0 && (
          <Text 
            fontSize="xs" 
            color="gray.500" 
            textAlign="center"
            fontFamily="'Microsoft YaHei', 'STHeiti', sans-serif"
          >
            {songCount} songs
          </Text>
        )}
      </Box>
    </LinkBox>
  );
};

export default CollectionCard; 