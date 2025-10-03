import React, { useState, useEffect } from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Button } from './ui/button';
import { ChevronLeft, ChevronRight, AlertTriangle, Loader2, Upload, FileJson, Search } from 'lucide-react';
import { Review } from '../data/mockData';
import { sampleReviews } from '../data/mockData';
import { listReviews, ensureSessionId, ingestReviews, searchReviews } from '../services/api';
import { toast } from 'sonner';

interface InboxPageProps {
  onSelectReview: (review: Review) => void;
}

export function InboxPage({ onSelectReview }: InboxPageProps) {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [sampleDataLoading, setSampleDataLoading] = useState(false);
  const [locationFilter, setLocationFilter] = useState<string>('all');
  const [sentimentFilter, setSentimentFilter] = useState<string>('all');
  const [topicFilter, setTopicFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchInput, setSearchInput] = useState<string>(''); // New state for input value
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [totalReviews, setTotalReviews] = useState<number>(0);
  const [locations, setLocations] = useState<string[]>([]);
  const [topics, setTopics] = useState<string[]>([]);

  const itemsPerPage = 5;

  // Ensure session ID exists
  useEffect(() => {
    ensureSessionId();
  }, []);

  // Fetch reviews
  useEffect(() => {
    fetchReviews();
  }, [locationFilter, sentimentFilter, topicFilter, searchQuery, currentPage]);

  const fetchReviews = async () => {
    setLoading(true);
    try {
      let response;

      if (searchQuery) {
        // For search, we want to show all most similar reviews without pagination
        const searchResults = await searchReviews(searchQuery);

        response = {
          reviews: searchResults,
          total: searchResults.length,
          page: 1,
          page_size: searchResults.length,
          total_pages: 1
        };
      } else {
        response = await listReviews(
          locationFilter === 'all' ? undefined : locationFilter,
          sentimentFilter === 'all' ? undefined : sentimentFilter,
          topicFilter === 'all' ? undefined : topicFilter,
          undefined, // No search query for list endpoint
          currentPage,
          itemsPerPage
        );
      }

      setReviews(response.reviews);
      setTotalReviews(response.total);
      setTotalPages(response.total_pages);

      const uniqueLocations = Array.from(new Set(response.reviews.map((r: Review) => r.location))) as string[];
      const uniqueTopics = Array.from(new Set(response.reviews.map((r: Review) => r.topic).filter(Boolean))) as string[];
      setLocations(uniqueLocations);
      setTopics(uniqueTopics);
    } catch (error) {
      toast.error('Failed to load reviews. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const content = await file.text();
      const reviewsData = JSON.parse(content);

      // Validate and ingest reviews
      if (Array.isArray(reviewsData)) {
        const sessionId = ensureSessionId();
        const reviewsWithSession = reviewsData.map((review: any) => ({
          ...review,
          session_id: sessionId,
          date: review.date || new Date().toISOString()
        }));

        await ingestReviews(reviewsWithSession);
        toast.success(`Successfully uploaded ${reviewsData.length} reviews!`);
        fetchReviews(); // Refresh the review list
      } else {
        toast.error('Invalid JSON format. Please upload a valid reviews array.');
      }
    } catch (error) {
      // Failed to upload reviews
      toast.error('Failed to upload reviews. Please check the file format.');
    }
  };

  const useSampleData = async () => {
    setSampleDataLoading(true);
    try {
      const sessionId = ensureSessionId();
      const reviewsWithSession = sampleReviews.map(review => ({
        ...review,
        session_id: sessionId
      }));

      await ingestReviews(reviewsWithSession);
      toast.success(`Successfully added ${sampleReviews.length} sample reviews!`);
      fetchReviews();
    } catch (error) {
      // Failed to add sample reviews
      toast.error('Failed to add sample reviews.');
    } finally {
      setSampleDataLoading(false);
    }
  };

  const getSentimentBadgeColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'negative': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'neutral': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const truncateText = (text: string, maxLength: number = 80) => {
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  const handleSearch = () => {
    if (searchInput.trim()) {
      setSearchQuery(searchInput.trim());
      setCurrentPage(1); // Reset to first page when searching
    } else {
      // If search input is empty, clear search results
      setSearchQuery('');
      setCurrentPage(1);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="space-y-4">
        <h1 className="gradient-text text-2xl">Review Inbox</h1>

        <Alert className="bg-yellow-500/10 border-yellow-500/30">
          <AlertTriangle className="h-4 w-4 text-yellow-400" />
          <AlertDescription className="text-yellow-300">
            ⚠️ Data is session-based and will be deleted 30 minutes after upload. Please upload a maximum of 15 reviews in 1 minute.
          </AlertDescription>
        </Alert>

        {/* Upload Section */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 flex gap-2">
            <Input
              placeholder="Search reviews..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              onKeyPress={handleKeyPress}
              className="bg-input border-border"
            />
            <Button onClick={handleSearch} className="bg-primary hover:bg-primary/90">
              <Search className="h-4 w-4" />
            </Button>
          </div>
          <div className="flex gap-2">
            <Button
              onClick={useSampleData}
              disabled={sampleDataLoading}
              className="bg-primary hover:bg-primary/90"
            >
              {sampleDataLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Loading Sample Data...
                </>
              ) : (
                <>
                  <FileJson className="h-4 w-4 mr-2" />
                  Use Sample Data
                </>
              )}
            </Button>
            <label className="cursor-pointer">
              <Input
                type="file"
                accept=".json"
                onChange={handleFileUpload}
                className="hidden"
              />
              <Button variant="outline" className="bg-card border-border hover:bg-muted">
                <Upload className="h-4 w-4 mr-2" />
                Upload JSON
              </Button>
            </label>
          </div>
        </div>

        <div className="flex flex-col md:flex-row gap-4">
          <Select value={locationFilter} onValueChange={setLocationFilter}>
            <SelectTrigger className="w-full md:w-48 bg-input border-border">
              <SelectValue placeholder="Filter by location" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Locations</SelectItem>
              {locations.map(location => (
                <SelectItem key={location} value={location}>{location}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={sentimentFilter} onValueChange={setSentimentFilter}>
            <SelectTrigger className="w-full md:w-48 bg-input border-border">
              <SelectValue placeholder="Filter by sentiment" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Sentiments</SelectItem>
              <SelectItem value="positive">Positive</SelectItem>
              <SelectItem value="neutral">Neutral</SelectItem>
              <SelectItem value="negative">Negative</SelectItem>
            </SelectContent>
          </Select>
          <Select value={topicFilter} onValueChange={setTopicFilter}>
            <SelectTrigger className="w-full md:w-48 bg-input border-border">
              <SelectValue placeholder="Filter by topic" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Topics</SelectItem>
              {topics.map(topic => (
                <SelectItem key={topic} value={topic}>{topic}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="bg-card border border-border rounded-lg overflow-hidden">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow className="border-border hover:bg-muted/50">
                <TableHead className="gradient-text">Location</TableHead>
                <TableHead className="gradient-text">Rating</TableHead>
                <TableHead className="gradient-text">Review</TableHead>
                <TableHead className="gradient-text">Sentiment</TableHead>
                <TableHead className="gradient-text">Topic</TableHead>
                <TableHead className="gradient-text">Date</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {reviews.map((review) => (
                <TableRow
                  key={review.id}
                  className="border-border hover:bg-muted/50 cursor-pointer"
                  onClick={() => onSelectReview(review)}
                >
                  <TableCell className="font-medium text-foreground">
                    {review.location}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      <span className="text-yellow-400">★</span>
                      <span className="text-foreground">{review.rating}</span>
                    </div>
                  </TableCell>
                  <TableCell className="max-w-md text-muted-foreground">
                    {truncateText(review.text)}
                  </TableCell>
                  <TableCell>
                    <Badge className={getSentimentBadgeColor(review.sentiment || '')}>
                      {review.sentiment || 'Unknown'}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30">
                      {review.topic || 'Unknown'}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {new Date(review.date).toLocaleDateString()}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>

      {!loading && totalPages > 1 && !searchQuery && (
        <div className="flex items-center justify-between">
          <p className="text-muted-foreground">
            Showing {(currentPage - 1) * itemsPerPage + 1} to {Math.min(currentPage * itemsPerPage, totalReviews)} of {totalReviews} reviews
          </p>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(page => Math.max(1, page - 1))}
              disabled={currentPage === 1}
              className="bg-card border-border hover:bg-muted"
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </Button>
            <span className="text-muted-foreground">
              Page {currentPage} of {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(page => Math.min(totalPages, page + 1))}
              disabled={currentPage === totalPages}
              className="bg-card border-border hover:bg-muted"
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}