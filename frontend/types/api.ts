export interface User { id: number; email: string; display_name: string; is_admin: boolean; is_active: boolean; created_at: string }
export interface LoginResponse { access_token: string; token_type: 'bearer'; user: User }
export interface Ingredient { amount: number | null; unit: string | null; name: string; note: string | null; scalable: boolean }
export interface RecipeDraft { name: string; description: string; servings: number; prep_minutes: number; cook_minutes: number; ingredients: Ingredient[]; instructions: string[]; tags: string[]; image_prompt: string | null }
export interface Health { status: 'ok'; openai_configured: boolean; mealie_configured: boolean }
export interface MealieCreateResponse { slug: string; image_status: 'uploaded' | 'skipped' | null }
export interface UserCreate { email: string; display_name: string; password: string; is_admin: boolean }
export interface UserUpdate { display_name?: string; is_active?: boolean; is_admin?: boolean }

