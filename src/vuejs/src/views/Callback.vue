<script setup>
    import { onMounted } from "vue";
    import { useRouter } from "vue-router";

    const router = useRouter();

    onMounted(() => {
        // Get the access token from the URL fragment
        const hash = window.location.hash.substring(1);
        const params = new URLSearchParams(hash);
        const token = params.get("access_token");
        if (token) {
            // Store token in localStorage (or Vuex/Pinia)
            localStorage.setItem("discord_token", token);
            // Redirect to home page
            router.push("/live-racing");
        } else {
            console.error("Authentication failed!");
            router.push("/live-racing");
        }
    });
</script>
