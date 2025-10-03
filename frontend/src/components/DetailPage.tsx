import { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Textarea } from './ui/textarea';
import { Loader2, Copy, ChevronLeft, Sparkles } from 'lucide-react';
import { Review } from '../data/mockData';
import { suggestReply } from '../services/api';
import { toast } from 'sonner';

interface DetailPageProps {
  review: Review;
  onBack: () => void;
  onReviewUpdate: (updatedReview: Review) => void;
}

interface AISuggestion {
  reply: string;
  reasoning_log: string;
}

export function DetailPage({ review, onBack, onReviewUpdate }: DetailPageProps) {
  const [aiLoading, setAiLoading] = useState(false);
  const [aiSuggestion, setAiSuggestion] = useState<AISuggestion | null>(null);
  const [replyText, setReplyText] = useState('');
  const [copied, setCopied] = useState(false);

  // Initialize reply text if review already has a reply
  useEffect(() => {
    if (review.reply) {
      setReplyText(review.reply);
      // We don't set aiSuggestion here because we don't have the full AI response data
    }
  }, [review]);

  const generateAIReply = async () => {
    setAiLoading(true);
    try {
      const suggestion = await suggestReply(review.id);
      setAiSuggestion(suggestion);
      setReplyText(suggestion.reply);

      // Update the review object with the new reply and notify parent
      const updatedReview = {
        ...review,
        reply: suggestion.reply
      };
      onReviewUpdate(updatedReview);

      toast.success('AI reply generated successfully!');
    } catch (error) {
      // Failed to generate AI reply
      toast.error('Failed to generate AI reply. Please try again.');
    } finally {
      setAiLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(replyText);
    setCopied(true);
    toast.success('Reply copied to clipboard!');
    setTimeout(() => setCopied(false), 2000);
  };

  const getSentimentBadgeColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'negative': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'neutral': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm" onClick={onBack} className="bg-card border-border hover:bg-muted">
          <ChevronLeft className="h-4 w-4 mr-2" />
          Back to Inbox
        </Button>
        <h1 className="gradient-text text-2xl">Review Details</h1>
      </div>

      <div className="space-y-6">
        {/* Review Details */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="gradient-text">Review Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">Location</h3>
                <p className="text-foreground">{review.location}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">Date</h3>
                <p className="text-foreground">{new Date(review.date).toLocaleDateString()}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">Rating</h3>
                <div className="flex items-center gap-1">
                  <span className="text-yellow-400">★</span>
                  <span className="text-foreground">{review.rating}/5</span>
                </div>
              </div>
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">Sentiment</h3>
                <Badge className={getSentimentBadgeColor(review.sentiment || '')}>
                  {review.sentiment || 'Unknown'}
                </Badge>
              </div>
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">Topic</h3>
                <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30">
                  {review.topic || 'Unknown'}
                </Badge>
              </div>
            </div>
            <div>
              <h3 className="text-sm font-medium text-muted-foreground">Review Text</h3>
              <p className="text-foreground mt-1">{review.text}</p>
            </div>
          </CardContent>
        </Card>

        {/* AI Reply Section */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="gradient-text flex items-center gap-2">
              <Sparkles className="h-5 w-5" />
              AI-Powered Reply
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {aiLoading ? (
              <div className="flex justify-center items-center h-32">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
            ) : (
              <>
                {replyText ? (
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-sm font-medium text-muted-foreground mb-2">Generated Reply</h3>
                      <Textarea
                        value={replyText}
                        onChange={(e) => setReplyText(e.target.value)}
                        rows={4}
                        className="bg-input border-border"
                      />
                    </div>

                    <div className="flex flex-wrap gap-2">
                      <Button onClick={copyToClipboard} variant="outline" className="bg-card border-border hover:bg-muted">
                        <Copy className={`h-4 w-4 mr-2 ${copied ? 'text-green-500' : ''}`} />
                        {copied ? 'Copied!' : 'Copy to Clipboard'}
                      </Button>
                    </div>

                    {aiSuggestion && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="md:col-span-2">
                          <h3 className="text-sm font-medium text-muted-foreground">Reasoning</h3>
                          <p className="text-foreground text-sm mt-1">{aiSuggestion.reasoning_log}</p>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="flex flex-col sm:flex-row gap-2">
                    <Button
                      onClick={generateAIReply}
                      disabled={aiLoading}
                      className="bg-primary hover:bg-primary/90"
                    >
                      <Sparkles className="h-4 w-4 mr-2" />
                      Generate AI Reply
                    </Button>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}