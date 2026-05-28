import { useState } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../contexts/AuthContext';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  FormErrorMessage,
  Heading,
  VStack,
  Text,
  Alert,
  AlertIcon,
  Container
} from '@chakra-ui/react';
import XiamiuLayout from '../components/Layout/XiamiuLayout';
import { useLanguage } from '../contexts/LanguageContext';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [usernameError, setUsernameError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  
  const router = useRouter();
  const { login, isAuthenticated } = useAuth();
  const { t } = useLanguage();
  
  // Redirect if already logged in
  if (isAuthenticated) {
    router.push('/');
    return null;
  }

  const validateForm = () => {
    let isValid = true;
    
    // Reset errors
    setUsernameError('');
    setPasswordError('');
    
    // Validate username
    if (!username.trim()) {
      setUsernameError(t('usernameRequired'));
      isValid = false;
    }
    
    // Validate password
    if (!password) {
      setPasswordError(t('passwordRequired'));
      isValid = false;
    }
    
    return isValid;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    setError('');
    
    try {
      const success = await login(username, password);
      
      if (success) {
        const returnUrl = router.query.returnUrl || '/';
        router.push(returnUrl);
      } else {
        setError(t('loginFailed'));
      }
    } catch (err) {
      setError(t('loginError'));
      console.error('Login error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <XiamiuLayout>
      <Container maxW="md" py={12}>
        <Box 
          p={8} 
          borderWidth={1} 
          borderRadius="lg" 
          boxShadow="lg"
          bg="white"
        >
          <VStack spacing={6} align="stretch">
            <Heading textAlign="center" size="lg" color="#f60">{t('loginToXiamiu')}</Heading>
            
            {error && (
              <Alert status="error" borderRadius="md">
                <AlertIcon />
                {error}
              </Alert>
            )}
            
            <form onSubmit={handleSubmit}>
              <VStack spacing={4}>
                <FormControl isInvalid={usernameError}>
                  <FormLabel>{t('username')}</FormLabel>
                  <Input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder={t('usernamePlaceholder')}
                  />
                  <FormErrorMessage>{usernameError}</FormErrorMessage>
                </FormControl>
                
                <FormControl isInvalid={passwordError}>
                  <FormLabel>{t('password')}</FormLabel>
                  <Input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder={t('passwordPlaceholder')}
                  />
                  <FormErrorMessage>{passwordError}</FormErrorMessage>
                </FormControl>
                
                <Button
                  type="submit"
                  colorScheme="orange"
                  width="full"
                  mt={4}
                  isLoading={isSubmitting}
                  loadingText={t('loggingIn')}
                >
                  {t('login')}
                </Button>
              </VStack>
            </form>
            
            <Text fontSize="sm" color="gray.600" textAlign="center">
              {t('registrationAdminOnly')}
            </Text>
          </VStack>
        </Box>
      </Container>
    </XiamiuLayout>
  );
} 
