# Feature Roadmap & Next Steps

_Last updated: 2025-04-24_

## 1. Mission & Strengths
- **Learner-driven content**: Users request exactly what they want to learn.
- **Instant feedback**: AI generates bite-sized vocab and exercises in seconds.
- **Lightweight UX**: No heavy downloads or textbooks—just conversational prompts.

## 2. Opportunity Areas
1. **Spaced Repetition & Memory Tracking**  
   - Store user performance on each word/phrase  
   - Re-surface items at optimal intervals
2. **Progress Metrics & Gamification**  
   - Streaks, points, badges, level progression  
   - Leaderboards or social sharing
3. **Multimedia Examples**  
   - TTS or native speaker audio clips for pronunciation  
   - Image or video context for vocabulary
4. **Error Handling & Fallbacks**  
   - Detect odd/irrelevant AI completions  
   - Rule-based retries or “Let me try that again” flow
5. **Cost Optimization**  
   - Cache common prompts/responses  
   - Rate-limit or batch requests when traffic spikes

## 3. Backend Enhancements
- **Logging & Analytics**  
  - Capture query patterns, response times, user success rates  
- **Prompt & Template Versioning**  
  - A/B test different prompt phrasings or lesson formats  
- **Async Processing & Scaling**  
  - Job queue for heavy tasks or high concurrency  
  - Request batching for OpenAI API calls

## 4. Next Steps
- ✔️ Capture and store user progress data  
- 📈 Build basic dashboard for user metrics  
- 🎧 Integrate TTS for pronunciation support  
- 🔄 Implement simple spaced-repetition algorithm  
- 🛠️ Set up caching layer for common prompts
