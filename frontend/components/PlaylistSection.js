import { Box, Flex, Text, SimpleGrid, useColorModeValue, Heading, Link } from '@chakra-ui/react';
import NextLink from 'next/link';
import { useLanguage } from '../contexts/LanguageContext';

const SectionHeader = ({ title, showMore = true }) => {
  const { t } = useLanguage();
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
              {t('more')}
            </Link>
          </NextLink>
        )}
      </Flex>
    </Flex>
  );
};

const PlaylistCategory = ({ title, active = false }) => {
  const activeBg = useColorModeValue('gray.800', 'gray.900');
  const inactiveBg = useColorModeValue('white', 'gray.700');
  const activeColor = useColorModeValue('white', 'white');
  const inactiveColor = useColorModeValue('gray.800', 'gray.100');
  
  return (
    <Box
      as={NextLink}
      href="#"
      px={4}
      py={2}
      bg={active ? activeBg : inactiveBg}
      color={active ? activeColor : inactiveColor}
      rounded="md"
      fontWeight={active ? 'bold' : 'normal'}
      textAlign="center"
      _hover={{
        bg: active ? activeBg : 'gray.100',
        textDecoration: 'none',
      }}
    >
      {title}
    </Box>
  );
};

const PlaylistSection = () => {
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const { t } = useLanguage();
  
  return (
    <Box mt={12} mb={8}>
      <SectionHeader title={t('playlistTitle')} />
      
      <Flex 
        justifyContent="center" 
        borderBottom="1px" 
        borderColor={borderColor}
        pb={4}
        mb={6}
      >
        <Flex gap={3} flexWrap="wrap" justifyContent="center">
          <PlaylistCategory title={t('mySubscriptions')} active={true} />
          <PlaylistCategory title={t('trendingUpdates')} />
          <PlaylistCategory title={t('musicianProjects')} />
          <PlaylistCategory title={t('birthday')} />
          <PlaylistCategory title={t('voiceActors')} />
          <PlaylistCategory title={t('newCentury')} />
        </Flex>
      </Flex>
      
      <Box textAlign="center" py={8}>
        <Text color="gray.500">{t('playlistComingSoon')}</Text>
      </Box>
    </Box>
  );
};

export default PlaylistSection; 
