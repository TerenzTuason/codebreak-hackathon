"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useLoading } from "@/context/LoadingContext";

export default function Home() {
  const router = useRouter();
  const { setIsLoading } = useLoading();

  useEffect(() => {
    const redirect = async () => {
      try {
        setIsLoading(true);
        await router.push("/login");
      } finally {
        setIsLoading(false);
      }
    };
    
    redirect();
  }, [router, setIsLoading]);

  return null; // No need to render anything as we're redirecting
}
