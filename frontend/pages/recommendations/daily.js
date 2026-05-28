import { useCallback, useEffect, useMemo, useState } from 'react';
import NextLink from 'next/link';
import {
  Alert,
  AlertDescription,
  AlertIcon,
  Badge,
  Box,
  Button,
  ButtonGroup,
  Collapse,
  Divider,
  Flex,
  FormControl,
  FormLabel,
  Grid,
  GridItem,
  HStack,
  Heading,
  IconButton,
  Link,
  SimpleGrid,
  Spinner,
  Stat,
  StatLabel,
  StatNumber,
  Text,
  Textarea,
  VStack,
  Wrap,
  WrapItem,
  useToast,
} from '@chakra-ui/react';
import { ChevronDownIcon, ChevronUpIcon, InfoOutlineIcon, RepeatIcon, StarIcon } from '@chakra-ui/icons';
import XiamiuLayout from '../../components/Layout/XiamiuLayout';
import { api } from '../../utils/api';
import { useLanguage } from '../../contexts/LanguageContext';

const normalizeItem = (item) => {
  const llm = item.llm || {};

  return {
    id: item.id || item.candidateId || item.candidate_id || item.album_id || item.albumId,
    rank: item.rank,
    albumId: item.album_id || item.albumId,
    artistName: item.artist_name || item.artistName,
    albumName: item.album_name || item.albumName,
    styles: item.styles || [],
    similarityScore: item.similarity_score ?? item.similarityScore,
    fitScore: item.fit_score ?? llm.fit_score,
    reason: item.reason || llm.reason,
    risk: item.risk ?? llm.risk,
    nearestNeighbors: item.nearest_neighbors || item.nearestRatedNeighbors || [],
    playCount: item.play_count ?? item.playCount,
    collects: item.collects,
    recommends: item.recommends,
    quickReaction: item.quick_reaction || item.quickReaction || null,
    feedback: item.feedback || null,
  };
};

const QUICK_REACTIONS = [
  { value: 'interested', labelKey: 'interested' },
  { value: 'save', labelKey: 'saveForLater' },
  { value: 'skip', labelKey: 'skip' },
];

const normalizeRecommendationSet = (data) => {
  const rawItems = data.items || data.recommendations || [];
  const items = rawItems.map((item, index) => ({
    ...normalizeItem(item),
    rank: item.rank || index + 1,
  }));

  return {
    id: data.id,
    generatedAt: data.generated_at || data.generatedAt,
    generationMethod: data.generation_method || data.generationMethod,
    embeddingModel: data.embedding_model || data.embeddingModel,
    judgeModel: data.judge_model || data.judgeModel,
    topN: data.top_n || data.topN || items.length,
    tasteProfileText: data.taste_profile_text || data.tasteProfileText,
    items,
  };
};

const formatDateTime = (value, language, fallback) => {
  if (!value) return fallback;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString(language === 'zh' ? 'zh-CN' : 'en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
};

const formatNumber = (value) => {
  if (value === null || value === undefined) return null;
  return new Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 }).format(value);
};

const formatScore = (value, digits = 1) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '—';
  return Number(value).toFixed(digits);
};

const RatingHistogram = ({ histogram }) => {
  if (!histogram || !Object.keys(histogram).length) return null;

  return (
    <HStack spacing={2} flexWrap="wrap">
      {[5, 4, 3, 2, 1].map((rating) => {
        const count = histogram[String(rating)] || histogram[rating];
        if (!count) return null;

        return (
          <Badge key={rating} colorScheme={rating >= 4 ? 'orange' : rating <= 2 ? 'red' : 'gray'}>
            {rating}★ × {count}
          </Badge>
        );
      })}
    </HStack>
  );
};

const EvidenceList = ({ neighbors }) => {
  const { t } = useLanguage();
  if (!neighbors.length) {
    return (
      <Text fontSize="sm" color="gray.500">
        {t('noNeighborEvidence')}
      </Text>
    );
  }

  return (
    <VStack align="stretch" spacing={3}>
      {neighbors.map((neighbor, index) => {
        const albumId = neighbor.album_id || neighbor.albumId;
        const artistName = neighbor.artist_name || neighbor.artistName;
        const albumName = neighbor.album_name || neighbor.albumName;
        const similarity = neighbor.similarity;
        const histogram = neighbor.rating_histogram || neighbor.ratingHistogram;

        return (
          <Box key={`${albumId || albumName}-${index}`} borderTopWidth={index === 0 ? '0' : '1px'} borderColor="gray.100" pt={index === 0 ? 0 : 3}>
            <Flex justify="space-between" align={{ base: 'start', md: 'center' }} gap={3} direction={{ base: 'column', md: 'row' }}>
              <Box>
                <Text fontSize="sm" fontWeight="bold">
                  {artistName} — {albumName}
                </Text>
                <Text fontSize="xs" color="gray.500">
                  {t('similarity')} {formatScore(similarity, 4)}
                </Text>
              </Box>
              <RatingHistogram histogram={histogram} />
            </Flex>
          </Box>
        );
      })}
    </VStack>
  );
};

const QuickReactionRow = ({ itemId, value, onChange }) => {
  const [busy, setBusy] = useState(false);
  const toast = useToast();
  const { t } = useLanguage();

  const handleClick = async (reaction) => {
    if (busy) return;
    const previous = value;
    onChange(reaction); // optimistic
    setBusy(true);
    try {
      const saved = await api.postQuickReaction(itemId, reaction);
      onChange(saved.reaction, saved);
    } catch (err) {
      onChange(previous); // revert
      toast({
        title: t('couldNotSaveReaction'),
        description: err?.response?.data?.detail || err?.message || t('unknownError'),
        status: 'error',
        duration: 4000,
        isClosable: true,
      });
    } finally {
      setBusy(false);
    }
  };

  return (
    <ButtonGroup size="sm" isAttached={false} spacing={2} flexWrap="wrap">
      {QUICK_REACTIONS.map(({ value: v, labelKey }) => {
        const active = value === v;
        return (
          <Button
            key={v}
            onClick={() => handleClick(v)}
            isLoading={busy && active}
            variant={active ? 'solid' : 'outline'}
            colorScheme={active ? 'orange' : 'gray'}
            borderColor={active ? '#f60' : 'gray.300'}
            color={active ? 'white' : 'gray.700'}
            bg={active ? '#f60' : 'white'}
            _hover={active ? { bg: 'orange.600' } : { bg: 'orange.50', borderColor: '#f60' }}
          >
            {t(labelKey)}
          </Button>
        );
      })}
    </ButtonGroup>
  );
};

const StarPicker = ({ value, onChange }) => {
  const { t } = useLanguage();
  return (
  <HStack spacing={1}>
    {[1, 2, 3, 4, 5].map((n) => (
      <IconButton
        key={n}
        aria-label={t('starCount', { count: n })}
        icon={<StarIcon />}
        size="sm"
        variant="ghost"
        color={n <= value ? '#f60' : 'gray.300'}
        onClick={() => onChange(n)}
        _hover={{ color: '#f60', bg: 'transparent' }}
      />
    ))}
  </HStack>
  );
};

const FeedbackPanel = ({ itemId, feedback, onSaved }) => {
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(!feedback);
  const [star, setStar] = useState(feedback?.star || 0);
  const [songImpression, setSongImpression] = useState(feedback?.song_impression || '');
  const [advice, setAdvice] = useState(feedback?.recommendation_advice || '');
  const [busy, setBusy] = useState(false);
  const toast = useToast();
  const { t } = useLanguage();

  useEffect(() => {
    if (feedback) {
      setStar(feedback.star || 0);
      setSongImpression(feedback.song_impression || '');
      setAdvice(feedback.recommendation_advice || '');
      setEditing(false);
    }
  }, [feedback]);

  const handleSubmit = async () => {
    if (star < 1 || star > 5) {
      toast({ title: t('pickStarsFirst'), status: 'warning', duration: 2500 });
      return;
    }
    setBusy(true);
    try {
      const saved = await api.postRecommendationFeedback(itemId, {
        star,
        song_impression: songImpression || null,
        recommendation_advice: advice || null,
      });
      onSaved(saved);
      setEditing(false);
      toast({ title: t('feedbackSaved'), status: 'success', duration: 2000 });
    } catch (err) {
      toast({
        title: t('couldNotSaveFeedback'),
        description: err?.response?.data?.detail || err?.message || t('unknownError'),
        status: 'error',
        duration: 4000,
        isClosable: true,
      });
    } finally {
      setBusy(false);
    }
  };

  const triggerLabel = feedback
    ? t('submittedEdit', { star: feedback.star })
    : t('rateThisRecommendation');

  return (
    <Box mt={3}>
      <Button
        size="sm"
        variant="ghost"
        color="#f60"
        leftIcon={open ? <ChevronUpIcon /> : <ChevronDownIcon />}
        onClick={() => setOpen(!open)}
        px={0}
        _hover={{ bg: 'transparent', color: 'orange.700' }}
      >
        {triggerLabel}
      </Button>
      <Collapse in={open} animateOpacity>
        <Box mt={3} p={4} bg="gray.50" borderRadius="md">
          {!editing && feedback ? (
            <VStack align="stretch" spacing={2}>
              <HStack>
                <Text fontSize="sm" fontWeight="bold" color="gray.600">{t('yourRating')}:</Text>
                <HStack spacing={0}>
                  {[1, 2, 3, 4, 5].map((n) => (
                    <StarIcon key={n} color={n <= feedback.star ? '#f60' : 'gray.300'} boxSize={4} />
                  ))}
                </HStack>
              </HStack>
              {feedback.song_impression && (
                <Box>
                  <Text fontSize="xs" color="gray.500" textTransform="uppercase" fontWeight="bold">{t('songImpression')}</Text>
                  <Text fontSize="sm">{feedback.song_impression}</Text>
                </Box>
              )}
              {feedback.recommendation_advice && (
                <Box>
                  <Text fontSize="xs" color="gray.500" textTransform="uppercase" fontWeight="bold">{t('recommendationAdvice')}</Text>
                  <Text fontSize="sm">{feedback.recommendation_advice}</Text>
                </Box>
              )}
              <Button size="xs" variant="link" color="#f60" alignSelf="start" onClick={() => setEditing(true)}>
                {t('editFeedback')}
              </Button>
            </VStack>
          ) : (
            <VStack align="stretch" spacing={3}>
              <FormControl>
                <FormLabel fontSize="sm" fontWeight="bold" color="gray.600" mb={1}>{t('yourRating')}</FormLabel>
                <StarPicker value={star} onChange={setStar} />
              </FormControl>
              <FormControl>
                <FormLabel fontSize="sm" fontWeight="bold" color="gray.600" mb={1}>
                  {t('whatDidYouThink')}
                </FormLabel>
                <Textarea
                  value={songImpression}
                  onChange={(e) => setSongImpression(e.target.value)}
                  placeholder={t('tasteProfilePlaceholder')}
                  size="sm"
                  resize="vertical"
                  bg="white"
                />
              </FormControl>
              <FormControl>
                <FormLabel fontSize="sm" fontWeight="bold" color="gray.600" mb={1}>
                  {t('futureAdvice')}
                </FormLabel>
                <Textarea
                  value={advice}
                  onChange={(e) => setAdvice(e.target.value)}
                  placeholder={t('judgeContextPlaceholder')}
                  size="sm"
                  resize="vertical"
                  bg="white"
                />
              </FormControl>
              <HStack justify="end">
                {feedback && (
                  <Button size="sm" variant="ghost" onClick={() => setEditing(false)} isDisabled={busy}>
                    {t('cancel')}
                  </Button>
                )}
                <Button size="sm" colorScheme="orange" onClick={handleSubmit} isLoading={busy}>
                  {t('submitFeedback')}
                </Button>
              </HStack>
            </VStack>
          )}
        </Box>
      </Collapse>
    </Box>
  );
};

const RecommendationCard = ({ item, onItemUpdate }) => {
  const [isEvidenceOpen, setIsEvidenceOpen] = useState(false);
  const playCount = formatNumber(item.playCount);
  const collects = formatNumber(item.collects);
  const recommends = formatNumber(item.recommends);
  const { t } = useLanguage();

  const updateQuickReaction = useCallback(
    (reactionValue, savedRow) => {
      const next = savedRow || (reactionValue ? { reaction: reactionValue } : null);
      onItemUpdate(item.id, { quickReaction: next });
    },
    [item.id, onItemUpdate]
  );

  const updateFeedback = useCallback(
    (savedRow) => {
      onItemUpdate(item.id, { feedback: savedRow });
    },
    [item.id, onItemUpdate]
  );

  return (
    <Box bg="white" borderWidth="1px" borderColor="gray.200" borderRadius="md" overflow="hidden">
      <Grid templateColumns={{ base: '1fr', lg: '92px 1fr 160px' }} gap={0}>
        <GridItem bg="gray.50" borderRightWidth={{ base: '0', lg: '1px' }} borderBottomWidth={{ base: '1px', lg: '0' }} borderColor="gray.200">
          <Flex h="100%" minH={{ base: '64px', lg: '100%' }} align="center" justify="center" direction={{ base: 'row', lg: 'column' }} gap={2} p={4}>
            <Text fontSize="xs" color="gray.500" fontWeight="bold" textTransform="uppercase">
              {t('rank')}
            </Text>
            <Text fontSize="3xl" fontWeight="bold" color="#f60" lineHeight="1">
              #{item.rank}
            </Text>
          </Flex>
        </GridItem>

        <GridItem p={{ base: 4, md: 5 }}>
          <Flex justify="space-between" align="start" gap={4} direction={{ base: 'column', md: 'row' }}>
            <Box>
              <Heading size="md" mb={1} color="black">
                {item.artistName} — {item.albumName}
              </Heading>
              <Wrap spacing={2} mb={3}>
                {item.styles.map((style) => (
                  <WrapItem key={style}>
                    <Badge colorScheme="orange" variant="subtle">
                      {style}
                    </Badge>
                  </WrapItem>
                ))}
              </Wrap>
            </Box>

            {item.albumId && (
              <NextLink href={`/albums/${item.albumId}`} passHref legacyBehavior>
                <Link color="#f60" fontSize="sm" fontWeight="bold" whiteSpace="nowrap">
                  {t('openAlbum')}
                </Link>
              </NextLink>
            )}
          </Flex>

          <Box mb={3}>
            <Text fontSize="xs" color="gray.500" textTransform="uppercase" fontWeight="bold" mb={1}>
              {t('whyThisFits')}
            </Text>
            <Text fontSize="sm" color="gray.800" lineHeight="1.7">
              {item.reason || t('noWrittenReason')}
            </Text>
          </Box>

          {item.risk && (
            <Alert status="warning" variant="left-accent" bg="orange.50" borderRadius="md" mb={3}>
              <AlertIcon color="#f60" />
              <AlertDescription fontSize="sm">{item.risk}</AlertDescription>
            </Alert>
          )}

          <Button
            size="sm"
            variant="ghost"
            color="#f60"
            leftIcon={isEvidenceOpen ? <ChevronUpIcon /> : <ChevronDownIcon />}
            onClick={() => setIsEvidenceOpen(!isEvidenceOpen)}
            px={0}
            _hover={{ bg: 'transparent', color: 'orange.700' }}
          >
            {t('similarRatedAlbums')}
          </Button>

          <Collapse in={isEvidenceOpen} animateOpacity>
            <Box mt={3} p={3} bg="gray.50" borderRadius="md">
              <EvidenceList neighbors={item.nearestNeighbors} />
            </Box>
          </Collapse>

          <Divider my={4} />

          <Box>
            <Text fontSize="xs" color="gray.500" textTransform="uppercase" fontWeight="bold" mb={2}>
              {t('quickReaction')}
            </Text>
            <QuickReactionRow
              itemId={item.id}
              value={item.quickReaction?.reaction || null}
              onChange={updateQuickReaction}
            />
          </Box>

          <FeedbackPanel
            itemId={item.id}
            feedback={item.feedback}
            onSaved={updateFeedback}
          />
        </GridItem>

        <GridItem bg="gray.50" borderLeftWidth={{ base: '0', lg: '1px' }} borderTopWidth={{ base: '1px', lg: '0' }} borderColor="gray.200">
          <VStack align="stretch" spacing={4} p={4} h="100%" justify="center">
            <Stat>
              <StatLabel fontSize="xs">{t('llmFit')}</StatLabel>
              <StatNumber color="#f60">{formatScore(item.fitScore)}</StatNumber>
            </Stat>
            <Stat>
              <StatLabel fontSize="xs">{t('embedding')}</StatLabel>
              <StatNumber fontSize="lg">{formatScore(item.similarityScore, 3)}</StatNumber>
            </Stat>
            <Divider />
            <SimpleGrid columns={3} spacing={2}>
              <Box>
                <Text fontSize="xs" color="gray.500">{t('plays')}</Text>
                <Text fontSize="sm" fontWeight="bold">{playCount || '—'}</Text>
              </Box>
              <Box>
                <Text fontSize="xs" color="gray.500">{t('saves')}</Text>
                <Text fontSize="sm" fontWeight="bold">{collects || '—'}</Text>
              </Box>
              <Box>
                <Text fontSize="xs" color="gray.500">{t('recs')}</Text>
                <Text fontSize="sm" fontWeight="bold">{recommends || '—'}</Text>
              </Box>
            </SimpleGrid>
          </VStack>
        </GridItem>
      </Grid>
    </Box>
  );
};

export default function DailyRecommendationsPage() {
  const [recommendations, setRecommendations] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const { language, t } = useLanguage();

  const loadRecommendations = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await api.getDailyRecommendations();
      setRecommendations(normalizeRecommendationSet(data));
    } catch (err) {
      console.error('Error loading daily recommendations:', err);
      setError(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadRecommendations();
  }, []);

  const handleItemUpdate = useCallback((itemId, patch) => {
    setRecommendations((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        items: prev.items.map((it) => (it.id === itemId ? { ...it, ...patch } : it)),
      };
    });
  }, []);

  const items = recommendations?.items || [];
  const generatedLabel = useMemo(
    () => formatDateTime(recommendations?.generatedAt, language, t('latestCachedRun')),
    [recommendations?.generatedAt, language, t]
  );
  const isEmpty404 = error?.response?.status === 404;

  const renderBody = () => {
    if (isLoading) {
      return (
        <Flex justify="center" align="center" minH="320px">
          <VStack spacing={4}>
            <Spinner size="xl" color="#f60" />
            <Text color="gray.500">{t('loadingCachedRecommendations')}</Text>
          </VStack>
        </Flex>
      );
    }

    if (error) {
      return (
        <Box bg="white" borderWidth="1px" borderRadius="md" p={8} textAlign="center">
          <InfoOutlineIcon boxSize={8} color={isEmpty404 ? '#f60' : 'red.400'} mb={4} />
          <Heading size="md" mb={3}>
            {isEmpty404 ? t('noRecommendationsYet') : t('recommendationsCouldNotLoad')}
          </Heading>
          <Text color="gray.600" mb={5}>
            {isEmpty404
              ? t('noRecommendationsHelp')
              : t('backendUnavailableHelp')}
          </Text>
          <Button leftIcon={<RepeatIcon />} colorScheme="orange" onClick={loadRecommendations}>
            {t('tryAgain')}
          </Button>
        </Box>
      );
    }

    if (!items.length) {
      return (
        <Box bg="white" borderWidth="1px" borderRadius="md" p={8} textAlign="center">
          <Heading size="md" mb={3}>{t('noRecommendationItems')}</Heading>
          <Text color="gray.600">{t('noRecommendationItemsHelp')}</Text>
        </Box>
      );
    }

    return (
      <VStack align="stretch" spacing={4}>
        {items.map((item) => (
          <RecommendationCard
            key={`${item.id}-${item.rank}`}
            item={item}
            onItemUpdate={handleItemUpdate}
          />
        ))}
      </VStack>
    );
  };

  return (
    <XiamiuLayout>
      <Box mb={6}>
        <Flex justify="space-between" align={{ base: 'start', md: 'end' }} direction={{ base: 'column', md: 'row' }} gap={4}>
          <Box>
            <Text color="#f60" fontWeight="bold" fontSize="sm" mb={1}>
              {t('dailyRecommendationsKicker')}
            </Text>
            <Heading size="lg" color="black" mb={2}>
              {t('cachedRecommendationSet')}
            </Heading>
            <Text color="gray.600" maxW="720px">
              {t('dailyRecommendationDescription')}
            </Text>
          </Box>

          <Box textAlign={{ base: 'left', md: 'right' }}>
            <Text fontSize="sm" color="gray.500">{t('generated')}</Text>
            <Text fontWeight="bold">{generatedLabel}</Text>
          </Box>
        </Flex>
      </Box>

      {recommendations && !isLoading && !error && (
        <SimpleGrid columns={{ base: 1, md: 4 }} spacing={4} mb={6}>
          <Box bg="white" borderWidth="1px" borderRadius="md" p={4}>
            <Text fontSize="xs" color="gray.500" textTransform="uppercase" fontWeight="bold">{t('items')}</Text>
            <Text fontSize="2xl" fontWeight="bold">{items.length}</Text>
          </Box>
          <Box bg="white" borderWidth="1px" borderRadius="md" p={4}>
            <Text fontSize="xs" color="gray.500" textTransform="uppercase" fontWeight="bold">{t('embedding')}</Text>
            <Text fontSize="sm" fontWeight="bold" noOfLines={1}>{recommendations.embeddingModel || 'BAAI/bge-m3'}</Text>
          </Box>
          <Box bg="white" borderWidth="1px" borderRadius="md" p={4}>
            <Text fontSize="xs" color="gray.500" textTransform="uppercase" fontWeight="bold">{t('judge')}</Text>
            <Text fontSize="sm" fontWeight="bold" noOfLines={1}>{recommendations.judgeModel || 'Cached LLM'}</Text>
          </Box>
          <Box bg="white" borderWidth="1px" borderRadius="md" p={4}>
            <Text fontSize="xs" color="gray.500" textTransform="uppercase" fontWeight="bold">{t('method')}</Text>
            <Text fontSize="sm" fontWeight="bold" noOfLines={1}>{recommendations.generationMethod || 'embedding + llm judge'}</Text>
          </Box>
        </SimpleGrid>
      )}

      {recommendations?.tasteProfileText && !isLoading && !error && (
        <Box bg="white" borderWidth="1px" borderRadius="md" mb={6} p={4}>
          <Button
            size="sm"
            variant="ghost"
            color="#f60"
            leftIcon={isProfileOpen ? <ChevronUpIcon /> : <ChevronDownIcon />}
            onClick={() => setIsProfileOpen(!isProfileOpen)}
            px={0}
            _hover={{ bg: 'transparent', color: 'orange.700' }}
          >
            {t('whyTheseRecommendations')}
          </Button>
          <Collapse in={isProfileOpen} animateOpacity>
            <Text mt={3} color="gray.700" lineHeight="1.7" fontSize="sm">
              {recommendations.tasteProfileText}
            </Text>
          </Collapse>
        </Box>
      )}

      {renderBody()}
    </XiamiuLayout>
  );
}
