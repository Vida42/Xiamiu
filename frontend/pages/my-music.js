import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { Box, Spinner, Flex, Container } from '@chakra-ui/react';
import XiamiuLayout from '../components/Layout/XiamiuLayout';
import { useAuth } from '../contexts/AuthContext';

export default function MyMusicRedirect() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading } = useAuth();

  // Redirect based on authentication status
  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated && user) {
        // Redirect to the user's personal my-music page
        router.replace(`/user/${user.id}/my-music`);
      } else {
        // Redirect to login with return URL
        router.replace(`/login?returnUrl=${encodeURIComponent(router.pathname)}`);
      }
    }
  }, [isLoading, isAuthenticated, user, router]);

  return (
    <XiamiuLayout>
      <Container maxW="container.xl">
        <Flex justifyContent="center" alignItems="center" minHeight="50vh">
          <Spinner size="xl" color="#f60" />
        </Flex>
      </Container>
    </XiamiuLayout>
  );
} 