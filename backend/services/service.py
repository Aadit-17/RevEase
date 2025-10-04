import asyncio
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import google.generativeai as genai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
from config import Config

from services.models import ReviewCreate, Review
from services.database import get_supabase_client

class ReviewService:
    def __init__(self):
        # Initialize Supabase client
        self.supabase = get_supabase_client()
        
        # Initialize Gemini API
        gemini_api_key = Config.GEMINI_API_KEY
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.5-flash-lite')
        else:
            self.gemini_model = None
    
    async def create_review(self, review_data: ReviewCreate) -> Review:
        """Create a new review"""
        review_dict = json.loads(review_data.json())
        
        review_dict['date'] = review_data.date.isoformat()
        if 'created_at' in review_dict and review_dict['created_at']:
            review_dict['created_at'] = review_data.created_at.isoformat() if review_data.created_at else None
        
        review_dict['session_id'] = str(review_data.session_id)
        
        if 'id' in review_dict:
            del review_dict['id']
        
        review_dict = {k: v for k, v in review_dict.items() if v is not None}
        
        # Insert into Supabase
        try:
            response = self.supabase.table("reviews").insert(review_dict).execute()
        except Exception as e:
            raise e
        
        if response.data:
            try:
                data = response.data[0]
                data['date'] = self._parse_datetime(data['date'])
                if 'created_at' in data and data['created_at']:
                    data['created_at'] = self._parse_datetime(data['created_at'])

                if 'id' in data:
                    data['id'] = int(data['id'])
                        
                if 'session_id' in data:
                    data['session_id'] = UUID(data['session_id'])

                review = Review(**data)
                
                asyncio.create_task(self._async_generate_ai_analysis(review))
                
                return review
            except Exception as e:
                # Fallback: create a basic review object with minimal data
                try:
                    data = response.data[0]
                    # Handle the ID conversion
                    review_id = int(data['id'])
                    session_id = UUID(data['session_id'])
                    
                    # Create review object
                    review = Review(
                        id=review_id,
                        session_id=session_id,
                        location=data['location'],
                        rating=data['rating'],
                        text=data['text'],
                        date=self._parse_datetime(data['date']),
                        sentiment=data.get('sentiment', ''),
                        topic=data.get('topic', ''),
                        reply=data.get('reply', ''),
                        created_at=self._parse_datetime(data['created_at']) if data.get('created_at') else None
                    )
                    
                    asyncio.create_task(self._async_generate_ai_analysis(review))
                    
                    return review
                except Exception as fallback_error:
                    # Fallback parsing also failed
                    raise Exception(f"Failed to parse review data: {e}")
        else:
            raise Exception("Failed to create review")
    
    def _parse_datetime(self, dt_string):
        """Parse datetime string from Supabase, handling various formats"""
        if isinstance(dt_string, datetime):
            return dt_string
        
        try:
            # Try direct parsing first
            return datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        except ValueError:
            try:
                # Handle format like '2025-10-03T14:45:47.33+00:00'
                if '.' in dt_string and '+' in dt_string:
                    # Split on '+' to get the timezone part
                    dt_part, tz_part = dt_string.rsplit('+', 1)
                    # If there's a fractional second, make sure it has 6 digits
                    if '.' in dt_part:
                        base_part, frac_part = dt_part.split('.')
                        # Pad fractional part to 6 digits
                        frac_part = frac_part.ljust(6, '0')[:6]
                        dt_part = f"{base_part}.{frac_part}"
                    # Reconstruct with proper format
                    formatted_string = f"{dt_part}+{tz_part}"
                    return datetime.fromisoformat(formatted_string)
                else:
                    # Try parsing with dateutil as a fallback
                    from dateutil import parser
                    return parser.isoparse(dt_string)
            except Exception:
                try:
                    # Try without timezone first
                    return datetime.fromisoformat(dt_string.replace('Z', ''))
                except Exception:
                    # If all else fails, return current time
                    return datetime.now()
    
    async def list_reviews(
        self,
        session_id: UUID,
        location: Optional[str] = None,
        sentiment: Optional[str] = None,
        topic: Optional[str] = None,
        search_query: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """List reviews with filters and pagination"""
        try:
            # Build query
            query = self.supabase.table("reviews").select("*").eq("session_id", str(session_id))
            
            # Apply filters
            if location:
                query = query.eq("location", location)
            
            if sentiment:
                query = query.eq("sentiment", sentiment)
            
            if topic and topic != "all":
                query = query.eq("topic", topic)
            
            if search_query:
                query = query.ilike("text", f"%{search_query}%")
            
            # Get total count
            count_response = query.execute()
            total = len(count_response.data) if count_response.data else 0
            
            # Apply pagination
            offset = (page - 1) * page_size
            query = query.range(offset, offset + page_size - 1)
            
            # Execute query
            response = query.execute()
        except Exception as e:
            raise e
        
        # Convert to Review models
        reviews = []
        if response.data:
            for review_data in response.data:
                try:
                    # Parse the datetime strings back to datetime objects
                    review_data['date'] = self._parse_datetime(review_data['date'])
                    if 'created_at' in review_data and review_data['created_at']:
                        review_data['created_at'] = self._parse_datetime(review_data['created_at'])
                    
                    # Convert IDs to proper types
                    if 'id' in review_data:
                        review_data['id'] = int(review_data['id'])
                            
                    if 'session_id' in review_data:
                        review_data['session_id'] = UUID(review_data['session_id'])
                    
                    reviews.append(Review(**review_data))
                except Exception as e:
                    # Error parsing review data
                    continue
        
        return {
            "reviews": reviews,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
        }
    
    async def get_review(self, review_id: int, session_id: UUID) -> Optional[Review]:
        """Get a specific review by ID"""
        try:
            response = self.supabase.table("reviews").select("*").eq("id", review_id).eq("session_id", str(session_id)).execute()
        except Exception as e:
            # Supabase query error
            raise e
        
        if response.data and len(response.data) > 0:
            try:
                # Parse the datetime strings back to datetime objects
                review_data = response.data[0]
                review_data['date'] = self._parse_datetime(review_data['date'])
                if 'created_at' in review_data and review_data['created_at']:
                    review_data['created_at'] = self._parse_datetime(review_data['created_at'])
                
                # Convert IDs to proper types
                if 'id' in review_data:
                    review_data['id'] = int(review_data['id'])
                        
                if 'session_id' in review_data:
                    review_data['session_id'] = UUID(review_data['session_id'])
                
                return Review(**review_data)
            except Exception as e:
                return None
        return None
    
    async def _async_generate_ai_analysis(self, review: Review):
        """Asynchronously generate AI analysis for sentiment only"""
        try:
            ai_response = await self.generate_ai_analysis(review)
            if ai_response and 'tags' in ai_response:
                sentiment = ai_response['tags'].get('sentiment', '')
                
                update_data = {
                    'sentiment': sentiment
                }
                self.supabase.table("reviews").update(update_data).eq("id", review.id).execute()
        except Exception as ai_error:
            pass

    async def generate_ai_analysis(self, review: Review) -> Dict[str, Any]:
        """Generate AI analysis (sentiment only) using Gemini API"""
        if not self.gemini_model:
            return self._get_rating_based_analysis(review)
        
        try:
            # Create prompt for Gemini
            prompt = f"""
            Analyze the sentiment of the following customer review:
            
            Location: {review.location}
            Rating: {review.rating}/5
            Review: {review.text}
            
            Provide analysis in JSON format:
            {{
                "tags": {{
                    "sentiment": "positive/neutral/negative"
                }},
                "reasoning_log": "brief explanation of your analysis"
            }}
            """
            
            # Generate response
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                self.gemini_model.generate_content, 
                prompt
            )
            
            # Parse response
            if response and response.text:
                try:
                    # Try to parse as JSON
                    result = json.loads(response.text)
                    return result
                except json.JSONDecodeError:
                    # If JSON parsing fails, fallback to rating-based sentiment
                    return self._get_rating_based_analysis(review)
            else:
                # Fallback response
                return self._get_rating_based_analysis(review)
        except Exception as e:
            # Fallback to rating-based sentiment on any API error
            return self._get_rating_based_analysis(review)
    
    def _get_rating_based_analysis(self, review: Review) -> Dict[str, Any]:
        """Fallback method to determine sentiment based on rating"""
        # Determine sentiment based on rating
        if review.rating >= 4:
            sentiment = "positive"
        elif review.rating <= 2:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "tags": {
                "sentiment": sentiment
            },
            "reasoning_log": f"Fallback analysis based on {review.rating} star rating"
        }
    
    async def generate_ai_reply(self, review: Review) -> Dict[str, Any]:
        """Generate AI reply using Gemini API"""
        if not self.gemini_model:
            # Fallback to template-based reply if no API key
            return self._get_template_based_reply(review)
        
        try:
            # Create prompt for Gemini
            prompt = f"""
            Generate an empathetic reply to the following customer review:
            
            Location: {review.location}
            Rating: {review.rating}/5
            Review: {review.text}
            
            Requirements:
            1. Be empathetic and professional
            2. Address specific points mentioned in the review
            3. Offer solutions if negative, or appreciation if positive
            4. Keep it concise (2-3 sentences)
            5. Do not make up facts about policies or procedures
            
            Respond with just the reply text.
            """
            
            # Generate response
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                self.gemini_model.generate_content, 
                prompt
            )
            
            # Extract reply text
            if response and response.text:
                reply_text = response.text
                
                return {
                    "reply": reply_text,
                    "reasoning_log": "Generated empathetic response to customer review"
                }
            else:
                # Fallback response
                return self._get_template_based_reply(review)
        except Exception as e:
            error_msg = f"Error generating AI response: {str(e)}"
            # Fallback to template-based reply on any API error
            return self._get_template_based_reply(review)
    
    def _get_template_based_reply(self, review: Review) -> Dict[str, Any]:
        """Fallback method to generate a template-based reply"""
        # Generate a reply based on the rating
        if review.rating >= 4:
            reply_text = f"Thank you for your positive feedback about our {review.location} location! We're thrilled to hear about your experience and look forward to serving you again soon."
        elif review.rating <= 2:
            reply_text = f"Thank you for bringing this to our attention regarding your experience at our {review.location} location. We apologize for any inconvenience and would like to make this right. A manager will reach out to you shortly to address your concerns."
        else:
            reply_text = f"Thank you for your feedback about our {review.location} location. We appreciate you taking the time to share your experience with us and will use this information to improve our services."
        
        return {
            "reply": reply_text,
            "reasoning_log": f"Template-based reply generated based on {review.rating} star rating"
        }
    
    def save_reply_to_db(self, review_id: int, reply_text: str):
        """Save reply to database in background"""
        try:
            update_data = {
                'reply': reply_text
            }
            self.supabase.table("reviews").update(update_data).eq("id", review_id).execute()
        except Exception as e:
            # Error updating reply in database
            pass
    
    async def get_analytics(self, session_id: UUID) -> Dict[str, Any]:
        """Get analytics for reviews"""
        try:
            # Get all reviews for this session
            response = self.supabase.table("reviews").select("*").eq("session_id", str(session_id)).execute()
        except Exception as e:
            # Supabase query error
            raise e
        
        reviews_data = response.data if response.data else []
        
        # Parse the datetime strings back to datetime objects
        reviews = []
        for review_data in reviews_data:
            try:
                review_data['date'] = self._parse_datetime(review_data['date'])
                if 'created_at' in review_data and review_data['created_at']:
                    review_data['created_at'] = self._parse_datetime(review_data['created_at'])
                
                # Convert IDs to proper types
                if 'id' in review_data:
                    review_data['id'] = int(review_data['id'])
                        
                if 'session_id' in review_data:
                    review_data['session_id'] = UUID(review_data['session_id'])
                
                reviews.append(review_data)
            except Exception as e:
                # Error parsing review data
                continue
        
        # Calculate sentiment distribution
        sentiment_counts = {}
        topic_counts = {}
        
        for review in reviews:
            # Sentiment distribution
            sentiment = review.get("sentiment", "unknown")
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            
            # Topic distribution
            topic = review.get("topic", "unknown")
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Format for response
        sentiment_data = [{"name": k, "value": v} for k, v in sentiment_counts.items()]
        topic_data = [{"topic": k, "count": v} for k, v in topic_counts.items()]
        
        return {
            "sentiment_distribution": sentiment_data,
            "topic_distribution": topic_data
        }
    
    async def search_reviews(self, session_id: UUID, query: str) -> List[Review]:
        """Search reviews using TF-IDF and cosine similarity"""
        try:
            # Get all reviews for this session
            response = self.supabase.table("reviews").select("*").eq("session_id", str(session_id)).execute()
        except Exception as e:
            # Supabase query error
            raise e
        
        reviews_data = response.data if response.data else []
        
        # Parse the datetime strings back to datetime objects
        reviews = []
        for review_data in reviews_data:
            try:
                review_data['date'] = self._parse_datetime(review_data['date'])
                if 'created_at' in review_data and review_data['created_at']:
                    review_data['created_at'] = self._parse_datetime(review_data['created_at'])
                
                # Convert IDs to proper types
                if 'id' in review_data:
                    review_data['id'] = int(review_data['id'])
                        
                if 'session_id' in review_data:
                    review_data['session_id'] = UUID(review_data['session_id'])
                
                reviews.append(Review(**review_data))
            except Exception as e:
                # Error parsing review data
                continue
        
        if not reviews:
            return []
        
        # Extract review texts
        review_texts = [review.text for review in reviews]
        
        # Add the search query to the corpus
        corpus = review_texts + [query]
        
        # Calculate TF-IDF vectors
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(corpus)
        
        # Calculate cosine similarity between query and all reviews
        cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()
        
        # Get indices of all reviews with their similarity scores
        similar_indices_scores = sorted(
            [(i, score) for i, score in enumerate(cosine_similarities)],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Take top 5 most similar reviews (or all if less than 5)
        top_similar = similar_indices_scores[:5]
        
        # Create result list with up to 5 reviews ordered by similarity
        results = []
        for idx, score in top_similar:
            if score > 0.005 and idx < len(reviews):
                results.append(reviews[idx])
        
        # Return exactly up to 5 reviews, even if similarity is low
        return results
    
    async def cleanup_old_reviews(self):
        """Delete reviews older than 30 minutes"""
        # This would typically be handled by a Supabase cron job or background task
        # Not implemented due to time constraints
        return 0
