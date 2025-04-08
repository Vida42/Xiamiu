import { Box, Image, Heading, Text, Badge, Stack, LinkBox, LinkOverlay, Flex } from '@chakra-ui/react';
import NextLink from 'next/link';
import { useEffect, useState } from 'react';
import { api } from '../../utils/api';

const SongCard = ({ song }) => {
  return (
    <LinkBox as="article">
      <Box
        p={2}
        borderWidth="1px"
        borderRadius="md"
        overflow="hidden"
        transition="transform 0.3s"
        _hover={{ transform: 'scale(1.03)', bg: 'gray.50' }}
      >
        <NextLink href={`/songs/${song.song_id}`} passHref legacyBehavior>
          <LinkOverlay>
            <Heading size="sm" mb={1}>{song.name}</Heading>
          </LinkOverlay>
        </NextLink>
        <Flex justifyContent="space-between" alignItems="center">
          <Text fontSize="xs" color="gray.500">Album: {song.album_id}</Text>
          <Badge colorScheme="yellow">
            {Array.from({ length: song.star }).map((_, i) => (
              <Text as="span" key={i} fontSize="10px">⭐</Text>
            ))}
          </Badge>
        </Flex>
      </Box>
    </LinkBox>
  );
};

export default SongCard; 