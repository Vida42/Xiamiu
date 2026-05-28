import { Box, Flex, Container, Link, Input, InputGroup, Text, Select, Button } from '@chakra-ui/react';
import NextLink from 'next/link';
import { SearchIcon } from '@chakra-ui/icons';
import { useRouter } from 'next/router';
import Head from 'next/head';
import { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';

const NavLink = ({ href, children, isActive }) => {
  return (
    <Box
      as={NextLink}
      href={href}
      px={{ base: 2, md: 4 }}
      py={2}
      _hover={{
        textDecoration: 'none',
        bg: 'rgba(255, 255, 255, 0.1)',
      }}
      color="white"
      display="block"
      whiteSpace="nowrap"
      fontSize={{ base: '13px', md: '14px' }}
      fontFamily="'Microsoft YaHei', 'STHeiti', sans-serif"
      fontWeight={isActive ? 'bold' : 'normal'}
    >
      {children}
    </Box>
  );
};

const SubNavLink = ({ href, children, isActive }) => {
  return (
    <Box
      as={NextLink}
      href={href}
      className={isActive ? "active" : ""}
      display="inline-block"
      height="100%"
      px={{ base: "14px", md: "20px" }}
      lineHeight="35px"
      fontSize="14px"
      whiteSpace="nowrap"
      textDecoration="none"
      _hover={{
        backgroundColor: "#e6e6e6",
        color: "#f60"
      }}
      backgroundColor={isActive ? "#e6e6e6" : "transparent"}
      color={isActive ? "#f60" : "#333"}
      fontFamily="'Microsoft YaHei', 'STHeiti', sans-serif"
    >
      {children}
    </Box>
  );
};

const XiamiuLayout = ({ children }) => {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState('general');
  const { user, isAuthenticated, logout } = useAuth();
  const { language, toggleLanguage, t } = useLanguage();

  // Handle search functionality
  const handleSearch = () => {
    const query = searchQuery.trim();
    if (query) {
      if (searchType === 'general') {
        router.push(`/search?q=${encodeURIComponent(query)}`);
      } else {
        router.push(`/search?q=${encodeURIComponent(query)}&type=${searchType}`);
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  // Handle my music link
  const handleMyMusicClick = (e) => {
    if (!isAuthenticated) {
      e.preventDefault();
      router.push('/login');
    }
  };

  // Check if current page is a detail page or an index page
  const isDetailPage = 
    router.pathname.includes('/artists/[id]') || 
    router.pathname.includes('/albums/[id]') || 
    router.pathname.includes('/songs/[id]') ||
    router.pathname.includes('/genres/[id]');

  // Check if the page has its own filtering mechanism (all index pages except home)
  const hasOwnFiltering =
    router.pathname === '/artists' ||
    router.pathname === '/albums' || 
    router.pathname === '/genres' ||
    router.pathname === '/songs';

  return (
    <Box fontFamily="'Microsoft YaHei', 'STHeiti', sans-serif">
      <Head>
        <title>Xiamiu Music</title>
        <style>{`
          @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap');
          
          body {
            font-family: 'Microsoft YaHei', 'STHeiti', 'Noto Sans SC', sans-serif;
          }
        `}</style>
      </Head>
      
      {/* Main Orange Navigation Bar (header-top) */}
      <Box className="header-top" bg="#f60">
        <Container maxW="container.xl">
          <Flex h="60px" alignItems="center" justifyContent="space-between" gap={{ base: 2, md: 4 }}>
            {/* Logo and Main Nav */}
            <Flex alignItems="center" gap={4}>
              <Box
                as={NextLink}
                href="/"
                fontSize="24px"
                fontWeight="bold"
                _hover={{ textDecoration: 'none' }}
                letterSpacing="tight"
                color="white"
              >
                Xiamiu
              </Box>
              <NavLink href="/" isActive={router.pathname === '/'}>
                {t('discoverMusic')}
              </NavLink>
              <NavLink 
                href={isAuthenticated ? `/user/${user?.id}/my-music` : "/my-music"} 
                isActive={router.pathname === '/my-music' || router.pathname.includes('/user/')}
                onClick={handleMyMusicClick}
              >
                {t('myMusic')}
              </NavLink>
            </Flex>

            {/* Search Bar with Type Selector - Show on all pages */}
              <Flex display={{ base: 'none', md: 'flex' }}>
              <InputGroup maxW="300px">
                <Input
                  placeholder={t('searchPlaceholder')}
                  bg="white"
                  color="gray.800"
                  _placeholder={{ color: 'gray.400' }}
                  onKeyDown={handleKeyDown}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  value={searchQuery}
                  borderRadius="full 0 0 full"
                  size="sm"
                />
              </InputGroup>
              <Select
                bg="white"
                color="gray.800"
                size="sm"
                width="120px"
                borderLeftRadius="0"
                borderRightRadius="0"
                value={searchType}
                onChange={(e) => setSearchType(e.target.value)}
                borderLeftColor="transparent"
              >
                <option value="general">{t('all')}</option>
                <option value="song">{t('songs')}</option>
                <option value="album">{t('albums')}</option>
                <option value="artist">{t('artists')}</option>
                <option value="genre">{t('genres')}</option>
              </Select>
              <Button 
                bg="white"
                size="sm"
                borderLeftRadius="0"
                borderRightRadius="full"
                onClick={handleSearch}
                px={2}
              >
                <SearchIcon color="gray.500" />
              </Button>
            </Flex>

            {/* Auth Links */}
            <Flex gap={4} align="center" display={{ base: 'none', md: 'flex' }}>
              <Button
                size="xs"
                variant="outline"
                color="white"
                borderColor="rgba(255,255,255,0.65)"
                borderRadius="full"
                px={3}
                minW="54px"
                _hover={{ bg: 'rgba(255,255,255,0.12)' }}
                onClick={toggleLanguage}
                aria-label={language === 'zh' ? 'Switch to English' : '切换到中文'}
              >
                {language === 'zh' ? 'EN' : '中文'}
              </Button>
              {isAuthenticated ? (
                <>
                  <Box
                    as={NextLink}
                    href={`/user/${user?.id}`}
                    color="white"
                    _hover={{ textDecoration: 'underline' }}
                    fontSize="14px"
                    fontWeight="medium"
                  >
                    {user?.user_name}
                  </Box>
                  <Box
                    as="button"
                    color="white"
                    _hover={{ textDecoration: 'underline' }}
                    fontSize="14px"
                    fontWeight="medium"
                    onClick={logout}
                  >
                    {t('logout')}
                  </Box>
                </>
              ) : (
                <>
                  <Box
                    as={NextLink}
                    href="/login"
                    color="white"
                    _hover={{ textDecoration: 'underline' }}
                    fontSize="14px"
                    fontWeight="medium"
                  >
                    {t('login')}
                  </Box>
                  <Box
                    as="button"
                    color="white"
                    _hover={{ textDecoration: 'underline' }}
                    fontSize="14px"
                    fontWeight="medium"
                    disabled={true}
                  >
                    {t('register')}
                  </Box>
                </>
              )}
            </Flex>
          </Flex>
        </Container>
      </Box>

      {/* Sub Navigation (header-bottom) */}
      <Box className="header-bottom" overflowX="auto">
        <Container maxW="container.xl">
          <Flex as="ul" className="nav" minW="max-content">
            <Box as="li">
              <SubNavLink href="/" isActive={router.pathname === '/'}>
                {t('popular')}
              </SubNavLink>
            </Box>
            <Box as="li">
              <SubNavLink href="/albums" isActive={router.pathname.startsWith('/albums')}>
                {t('albums')}
              </SubNavLink>
            </Box>
            <Box as="li">
              <SubNavLink href="/artists" isActive={router.pathname.startsWith('/artists')}>
                {t('artists')}
              </SubNavLink>
            </Box>
            <Box as="li">
              <SubNavLink href="/genres" isActive={router.pathname.startsWith('/genres')}>
                {t('genres')}
              </SubNavLink>
            </Box>
            <Box as="li">
              <SubNavLink href="/recommendations/daily" isActive={router.pathname.startsWith('/recommendations')}>
                {t('aiRecommendations')}
              </SubNavLink>
            </Box>
          </Flex>
        </Container>
      </Box>

      {/* Main Content */}
      <Container maxW="container.xl" py={6}>
        {children}
      </Container>

      {/* Footer */}
      <Box bg="white" py={8} borderTop="1px" borderColor="gray.200">
        <Container maxW="container.xl">
          <Flex justifyContent="center" mb={4}>
            <Box
              as={NextLink} 
              href="/"
              color="gray.500"
              fontSize="sm"
              _hover={{ color: '#f60' }}
            >
              © {new Date().getFullYear()} Xiamiu Music
            </Box>
          </Flex>
        </Container>
      </Box>
    </Box>
  );
};

export default XiamiuLayout;
