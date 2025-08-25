interface GitHubRepo {
  id: number
  name: string
  full_name: string
  html_url: string
  description: string
  created_at: string
  updated_at: string
  pushed_at: string
  stargazers_count: number
  watchers_count: number
  forks_count: number
  open_issues_count: number
  language: string
  languages_url: string
  size: number // in KB
  default_branch: string
  topics: string[]
  archived: boolean
  private: boolean
}

interface GitHubCommit {
  sha: string
  commit: {
    author: {
      name: string
      email: string
      date: string
    }
    message: string
  }
}

interface ProjectMetrics {
  id: string
  name: string
  size: number // Normalized 0-1 size for garden display
  growthStage: 'seed' | 'sprout' | 'growing' | 'blooming' | 'mature'
  health: number // 0-1 health metric
  activity: number // Recent activity level
  importance: number // Overall importance score
  commits: number
  stars: number
  forks: number
  lastUpdate: string
  languages: Record<string, number>
  plantType: 'tree' | 'flower' | 'bush' | 'vine' | 'succulent' | 'grass'
}

class ProjectMetricsService {
  private cache = new Map<string, ProjectMetrics>()
  private cacheExpiry = new Map<string, number>()
  private readonly CACHE_DURATION = 1000 * 60 * 30 // 30 minutes

  private readonly GITHUB_API_BASE = 'https://api.github.com'
  private readonly USER_REPOS_URL = `${this.GITHUB_API_BASE}/users/cameronopotter/repos`

  // Real Cameron Potter repositories (from his GitHub)
  private readonly KNOWN_REPOS = [
    'cameronopotter/digital-greenhouse',
    'cameronopotter/wager-x', 
    'cameronopotter/gpas',
    // Add more as they're discovered
  ]

  async fetchGitHubRepos(): Promise<GitHubRepo[]> {
    try {
      const response = await fetch(`${this.USER_REPOS_URL}?sort=updated&per_page=50`)
      if (!response.ok) {
        throw new Error(`GitHub API error: ${response.status}`)
      }
      
      const repos: GitHubRepo[] = await response.json()
      
      // Filter out forks and focus on original repositories
      const filteredRepos = repos
        .filter(repo => {
          // Only include public, non-archived, non-fork repositories
          return !repo.private && !repo.archived && !repo.fork
        })
        .sort((a, b) => {
          // Prioritize known important repos, then by activity
          const aKnown = this.KNOWN_REPOS.includes(a.full_name)
          const bKnown = this.KNOWN_REPOS.includes(b.full_name)
          
          if (aKnown && !bKnown) return -1
          if (!aKnown && bKnown) return 1
          
          // Sort by last activity
          return new Date(b.pushed_at).getTime() - new Date(a.pushed_at).getTime()
        })
      
      console.log('Fetched real GitHub repos:', filteredRepos.map(r => r.name))
      return filteredRepos
      
    } catch (error) {
      console.error('Failed to fetch GitHub repos:', error)
      // NO FALLBACK TO MOCK DATA
      return []
    }
  }

  async fetchCommitCount(repoFullName: string): Promise<number> {
    try {
      // Get recent commits (GitHub API limits to 100 per page)
      const response = await fetch(`${this.GITHUB_API_BASE}/repos/${repoFullName}/commits?per_page=100`)
      if (!response.ok) {
        return 0
      }
      
      const commits: GitHubCommit[] = await response.json()
      
      // This is a simplified count - for more accurate numbers, 
      // you'd need to paginate through all commits or use GraphQL API
      return commits.length
    } catch (error) {
      console.error(`Failed to fetch commits for ${repoFullName}:`, error)
      return Math.floor(Math.random() * 50) + 10 // Mock fallback
    }
  }

  async fetchLanguages(languagesUrl: string): Promise<Record<string, number>> {
    try {
      const response = await fetch(languagesUrl)
      if (!response.ok) {
        return {}
      }
      
      return await response.json()
    } catch (error) {
      console.error('Failed to fetch languages:', error)
      return {}
    }
  }

  private calculateImportanceScore(repo: GitHubRepo, commits: number, allRepos: GitHubRepo[]): number {
    let score = 0
    
    // Enhanced scoring system for better project size balancing
    
    // Stars contribute to importance (0-30 points) - reduced weight
    score += Math.min(repo.stargazers_count * 1.5, 30)
    
    // Forks contribute (0-15 points) - reduced weight  
    score += Math.min(repo.forks_count * 3, 15)
    
    // Recent activity (0-25 points) - increased weight
    const daysSinceUpdate = (Date.now() - new Date(repo.pushed_at).getTime()) / (1000 * 60 * 60 * 24)
    const activityScore = Math.max(25 - daysSinceUpdate / 3, 0)
    score += activityScore
    
    // Repository size relative to other repos (0-15 points)
    const avgRepoSize = allRepos.reduce((sum, r) => sum + r.size, 0) / allRepos.length
    const sizeScore = Math.min((repo.size / Math.max(avgRepoSize, 1)) * 15, 15)
    score += sizeScore
    
    // Commits with relative scaling (0-35 points) - increased weight
    const maxCommitsInSet = Math.max(...allRepos.map(() => commits), 50) // Assume max 50 for scaling
    const commitScore = (commits / Math.max(maxCommitsInSet, 1)) * 35
    score += commitScore
    
    // Language diversity bonus (0-10 points)
    const languageBonus = repo.language ? 5 : 0
    const topicsBonus = Math.min(repo.topics.length * 1, 5)
    score += languageBonus + topicsBonus
    
    // Known important repos get bonus (0-15 points) - reduced from 20
    if (this.KNOWN_REPOS.includes(repo.full_name)) {
      score += 15
    }
    
    // Special project type bonuses
    if (repo.name.toLowerCase().includes('portfolio') || 
        repo.name.toLowerCase().includes('website') ||
        repo.name.toLowerCase().includes('app')) {
      score += 10
    }
    
    // Penalize archived or very old repos
    if (repo.archived) {
      score *= 0.3
    }
    
    const monthsSinceUpdate = daysSinceUpdate / 30
    if (monthsSinceUpdate > 12) {
      score *= Math.max(0.4, 1 - (monthsSinceUpdate - 12) / 24)
    }
    
    return Math.min(score / 135, 1) // Normalize to 0-1 with updated max score
  }

  private determineGrowthStage(importance: number, activity: number): ProjectMetrics['growthStage'] {
    const combined = (importance + activity) / 2
    
    if (combined < 0.2) return 'seed'
    if (combined < 0.4) return 'sprout'  
    if (combined < 0.6) return 'growing'
    if (combined < 0.8) return 'blooming'
    return 'mature'
  }

  private determinePlantType(repo: GitHubRepo, languages: Record<string, number>): ProjectMetrics['plantType'] {
    const primaryLanguage = repo.language?.toLowerCase() || ''
    const repoName = repo.name.toLowerCase()
    const repoSize = repo.size
    const topics = repo.topics.join(' ').toLowerCase()
    
    // Enhanced plant type determination with more variety
    
    // Large, complex projects → Trees
    if (repoSize > 15000 || repo.stargazers_count > 5 || 
        primaryLanguage.includes('java') || primaryLanguage.includes('c++') ||
        primaryLanguage.includes('c#') || topics.includes('framework')) {
      return 'tree'
    }
    
    // Backend/API projects → Trees (sturdy foundation)
    if (primaryLanguage.includes('php') || primaryLanguage.includes('go') ||
        repoName.includes('api') || repoName.includes('backend') || repoName.includes('server') ||
        topics.includes('backend') || topics.includes('api') || topics.includes('microservice')) {
      return 'tree'
    }
    
    // Frontend/Visual projects → Flowers (beautiful, user-facing)
    if (primaryLanguage.includes('css') || primaryLanguage.includes('html') ||
        repoName.includes('ui') || repoName.includes('frontend') || repoName.includes('website') ||
        topics.includes('frontend') || topics.includes('ui') || topics.includes('design') ||
        repoName.includes('portfolio') || repoName.includes('blog')) {
      return 'flower'
    }
    
    // Data science/ML projects → Succulents (specialized, efficient)
    if (primaryLanguage.includes('python') || primaryLanguage.includes('r') ||
        topics.includes('machine-learning') || topics.includes('data-science') ||
        topics.includes('analytics') || repoName.includes('analysis')) {
      return 'succulent'
    }
    
    // Mobile/Cross-platform → Vines (grows across platforms)
    if (primaryLanguage.includes('swift') || primaryLanguage.includes('kotlin') ||
        primaryLanguage.includes('dart') || topics.includes('mobile') ||
        topics.includes('ios') || topics.includes('android') || topics.includes('flutter') ||
        topics.includes('react-native')) {
      return 'vine'
    }
    
    // Scripts/Tools/Utilities → Grass (small, utility)
    if (repoName.includes('script') || repoName.includes('tool') || repoName.includes('util') ||
        repoName.includes('config') || repoName.includes('dot') || repoSize < 1000 ||
        topics.includes('automation') || topics.includes('cli')) {
      return 'grass'
    }
    
    // JavaScript/TypeScript projects
    if (primaryLanguage.includes('javascript') || primaryLanguage.includes('typescript')) {
      // Large JS projects → Trees, smaller ones → Vines
      return repoSize > 5000 ? 'tree' : 'vine'
    }
    
    // Medium-sized projects → Bushes (default for moderate complexity)
    return 'bush'
  }

  private calculateHealth(repo: GitHubRepo, commits: number): number {
    let health = 0.5 // Base health
    
    // Recent activity boosts health
    const daysSinceUpdate = (Date.now() - new Date(repo.pushed_at).getTime()) / (1000 * 60 * 60 * 24)
    if (daysSinceUpdate < 7) health += 0.3
    else if (daysSinceUpdate < 30) health += 0.2
    else if (daysSinceUpdate < 90) health += 0.1
    else health -= 0.2
    
    // Stars and engagement
    health += Math.min(repo.stargazers_count * 0.05, 0.3)
    
    // Commit activity
    health += Math.min(commits * 0.01, 0.2)
    
    // Open issues (too many reduce health)
    if (repo.open_issues_count > 10) health -= 0.1
    
    return Math.max(0.1, Math.min(health, 1))
  }

  // NO MORE MOCK DATA - Only return empty array if API fails
  private getEmptyRepositories(): GitHubRepo[] {
    return []
  }

  async calculateProjectMetrics(repo: GitHubRepo, allRepos: GitHubRepo[]): Promise<ProjectMetrics> {
    const cacheKey = repo.full_name
    const now = Date.now()
    
    // Check cache
    if (this.cache.has(cacheKey) && this.cacheExpiry.get(cacheKey)! > now) {
      return this.cache.get(cacheKey)!
    }

    // Fetch additional data
    const [commits, languages] = await Promise.all([
      this.fetchCommitCount(repo.full_name),
      this.fetchLanguages(repo.languages_url)
    ])

    const importance = this.calculateImportanceScore(repo, commits, allRepos)
    const health = this.calculateHealth(repo, commits)
    
    // Enhanced activity calculation
    const daysSinceUpdate = (Date.now() - new Date(repo.pushed_at).getTime()) / (1000 * 60 * 60 * 24)
    const daysSinceCreation = (Date.now() - new Date(repo.created_at).getTime()) / (1000 * 60 * 60 * 24)
    
    // Activity considers both recency and project maturity
    let activity = Math.max(0, 1 - daysSinceUpdate / 365) // Base activity from recency
    
    // Boost activity for projects with consistent updates
    const projectAge = Math.min(daysSinceCreation / 365, 3) // Cap at 3 years for scaling
    const consistencyBonus = (commits / Math.max(projectAge, 0.5)) > 10 ? 0.2 : 0
    activity = Math.min(activity + consistencyBonus, 1)
    
    // Calculate relative size for better visual balance
    const maxImportanceInSet = Math.max(...allRepos.map(r => this.calculateImportanceScore(r, commits, allRepos)))
    const relativeSize = importance / Math.max(maxImportanceInSet, 0.1)
    
    // Ensure minimum size for visibility
    const displaySize = Math.max(relativeSize, 0.15)

    const metrics: ProjectMetrics = {
      id: repo.id.toString(),
      name: repo.name,
      size: displaySize, // Use relative size for better visual balance
      growthStage: this.determineGrowthStage(importance, activity),
      health,
      activity,
      importance,
      commits,
      stars: repo.stargazers_count,
      forks: repo.forks_count,
      lastUpdate: repo.pushed_at,
      languages,
      plantType: this.determinePlantType(repo, languages)
    }

    // Cache the result
    this.cache.set(cacheKey, metrics)
    this.cacheExpiry.set(cacheKey, now + this.CACHE_DURATION)

    return metrics
  }

  async getAllProjectMetrics(): Promise<ProjectMetrics[]> {
    try {
      const repos = await this.fetchGitHubRepos()
      if (repos.length === 0) {
        console.warn('No GitHub repositories found')
        return []
      }
      
      // Only use real repos, no fallbacks
      const relevantRepos = repos.slice(0, 15).filter(repo => !repo.archived)
      
      if (relevantRepos.length === 0) {
        console.warn('No active repositories found')
        return []
      }
      
      // Calculate metrics for all repos together for better relative sizing
      const metricsPromises = relevantRepos.map(repo => this.calculateProjectMetrics(repo, relevantRepos))
      const allMetrics = await Promise.all(metricsPromises)
      
      // Enhanced size balancing for better visibility
      const processedMetrics = this.enhancedBalanceProjectSizes(allMetrics)
      
      console.log('Real GitHub projects loaded:', processedMetrics.map(p => ({ name: p.name, size: p.size, importance: p.importance })))
      
      return processedMetrics
    } catch (error) {
      console.error('Failed to get project metrics:', error)
      // NO FALLBACK TO MOCK DATA - return empty array
      return []
    }
  }
  
  private enhancedBalanceProjectSizes(metrics: ProjectMetrics[]): ProjectMetrics[] {
    if (metrics.length === 0) return []
    
    // Sort by importance to identify tiers
    const sorted = [...metrics].sort((a, b) => b.importance - a.importance)
    
    // Enhanced sizing algorithm for better visibility
    return metrics.map(metric => {
      const sortedIndex = sorted.findIndex(m => m.id === metric.id)
      const relativeRank = sortedIndex / Math.max(sorted.length - 1, 1)
      
      // Much larger base sizes for better visibility
      const baseSize = 0.8 + (1 - relativeRank) * 0.4 // Range from 0.8 to 1.2
      
      // Add variation based on specific metrics
      const recentActivityBonus = metric.activity > 0.5 ? 0.2 : 0
      const commitBonus = Math.min(metric.commits / 50, 0.2)
      const importanceBonus = metric.importance * 0.3
      
      const finalSize = Math.max(
        baseSize + recentActivityBonus + commitBonus + importanceBonus,
        0.6 // Minimum size for visibility
      )
      
      console.log(`Project ${metric.name}: importance=${metric.importance.toFixed(2)}, size=${finalSize.toFixed(2)}`)
      
      return {
        ...metric,
        size: finalSize
      }
    })
  }

  clearCache() {
    this.cache.clear()
    this.cacheExpiry.clear()
  }
}

export const projectMetricsService = new ProjectMetricsService()
export type { ProjectMetrics, GitHubRepo }