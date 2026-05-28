export const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return 'N/A';
    
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'N/A';
  }
};

export const formatHtmlInfo = (value) => {
  if (!value) return '';

  const text = removeOfficeTags(String(value))
    .replace(/&nbsp;|\u00a0/gi, ' ')
    .replace(/>\s+</g, '><')
    .replace(/<\s*br\s*\/?>/gi, '\n')
    .replace(/<\s*\/\s*(p|div|li|h[1-6])\s*>/gi, '\n')
    .replace(/<\s*(p|div|li|h[1-6])(\s[^>]*)?>/gi, '')
    .replace(/<[^>]+>/g, '');

  return cleanInfoText(decodeHtmlEntities(text));
};

export const sanitizeHtmlInfo = (value) => {
  if (!value) return '';

  const allowedTags = new Set(['strong', 'b', 'em', 'i', 'br', 'p', 'div', 'ul', 'ol', 'li']);
  const input = removeOfficeTags(String(value)).replace(/&nbsp;|\u00a0/gi, ' ').replace(/>\s+</g, '><');
  let output = '';
  let cursor = 0;

  for (const match of input.matchAll(/<[^>]*>/g)) {
    output += escapeHtml(cleanInfoText(decodeHtmlEntities(input.slice(cursor, match.index))));
    output += sanitizeTag(match[0], allowedTags);
    cursor = match.index + match[0].length;
  }

  output += escapeHtml(cleanInfoText(decodeHtmlEntities(input.slice(cursor))));

  return output.trim();
};

export const getLocalizedInfo = (record, language) => {
  if (!record) return '';

  const preferred = language === 'zh' ? record.info_zh : record.info_en;
  const secondary = language === 'zh' ? record.info_en : record.info_zh;

  return preferred || record.info || secondary || '';
};

const cleanInfoText = (value) => {
  return removeOfficeTags(String(value))
    .replace(/([\u4e00-\u9fff])[ \t]+([\u4e00-\u9fff])[ \t]+([\u4e00-\u9fff])(?=[ \t]|$)/g, '$1$2$3')
    .replace(/([\u4e00-\u9fff])[ \t]+([\u4e00-\u9fff])(?=[ \t]|$)/g, '$1$2')
    .replace(/[ \t]+\n/g, '\n')
    .replace(/\n[ \t]+/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .replace(/[ \t]{2,}/g, ' ')
    .trim();
};

const removeOfficeTags = (value) => {
  return String(value)
    .replace(/<\s*\/?\s*o:p\s*\/?\s*>/gi, '')
    .replace(/&lt;\s*\/?\s*o:p\s*\/?\s*&gt;/gi, '');
};

const sanitizeTag = (tag, allowedTags) => {
  const tagName = tag.match(/^<\s*\/?\s*([a-z0-9]+)/i)?.[1]?.toLowerCase();
  if (!tagName || !allowedTags.has(tagName)) return '';
  if (tagName === 'br') return '<br />';
  return /^<\s*\//.test(tag) ? `</${tagName}>` : `<${tagName}>`;
};

const decodeHtmlEntities = (value) => {
  return String(value)
    .replace(/&amp;/gi, '&')
    .replace(/&lt;/gi, '<')
    .replace(/&gt;/gi, '>')
    .replace(/&quot;/gi, '"')
    .replace(/&ldquo;/gi, '“')
    .replace(/&rdquo;/gi, '”')
    .replace(/&lsquo;/gi, '‘')
    .replace(/&rsquo;/gi, '’')
    .replace(/&mdash;/gi, '—')
    .replace(/&ndash;/gi, '–')
    .replace(/&hellip;/gi, '…')
    .replace(/&middot;/gi, '·')
    .replace(/&bull;/gi, '•')
    .replace(/&copy;/gi, '©')
    .replace(/&reg;/gi, '®')
    .replace(/&trade;/gi, '™')
    .replace(/&#39;/g, "'")
    .replace(/&#x([0-9a-f]+);/gi, (_, code) => String.fromCharCode(parseInt(code, 16)))
    .replace(/&#(\d+);/g, (_, code) => String.fromCharCode(Number(code)));
};

const escapeHtml = (value) => {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
};
