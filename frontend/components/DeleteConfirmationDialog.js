import {
  AlertDialog,
  AlertDialogBody,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogContent,
  AlertDialogOverlay,
  Button
} from '@chakra-ui/react';
import { useRef } from 'react';
import { useLanguage } from '../contexts/LanguageContext';

const DeleteConfirmationDialog = ({ 
  isOpen, 
  onClose, 
  onDelete, 
  title,
  description
}) => {
  const cancelRef = useRef();
  const { t } = useLanguage();

  return (
    <AlertDialog
      isOpen={isOpen}
      leastDestructiveRef={cancelRef}
      onClose={onClose}
    >
      <AlertDialogOverlay>
        <AlertDialogContent>
          <AlertDialogHeader fontSize="lg" fontWeight="bold">
            {title || t('deleteComment')}
          </AlertDialogHeader>

          <AlertDialogBody>
            {description || t('deleteCommentConfirm')}
          </AlertDialogBody>

          <AlertDialogFooter>
            <Button ref={cancelRef} onClick={onClose}>
              {t('cancel')}
            </Button>
            <Button colorScheme="red" onClick={onDelete} ml={3}>
              {t('delete')}
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialogOverlay>
    </AlertDialog>
  );
};

export default DeleteConfirmationDialog; 
