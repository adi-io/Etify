import { createClient } from "@/utils/supabase/server";

export default async function signOut() {
    const supabase = await createClient();
    const { error } = await supabase.auth.signOut();
    if (error) {
        console.error(error);
        return <p>Sorry, something went wrong</p>;
    }
    return <p>You have been signed out</p>;
}
