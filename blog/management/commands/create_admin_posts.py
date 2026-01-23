"""Django Management Command to Create Admin User and 30 Posts"""

import random
import urllib.request
from io import BytesIO
from typing import Any
from urllib.parse import urlparse

from django.core.files import File
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.db import transaction

from blog.models import Category, Post


class Command(BaseCommand):
    """Command to create admin user and 30 posts with online images"""

    help = "Creates admin user 'Surya' with password '12345678' and 30 posts with online images"

    def handle(self, *args: Any, **options):
        """Main handler for the command"""
        
        # Step 1: Create or get admin user
        self.stdout.write("Creating admin user...")
        user, created = User.objects.get_or_create(
            username="Surya",
            defaults={
                "email": "surya@example.com",
                "first_name": "Surya",
                "last_name": "Admin",
                "is_staff": True,
                "is_superuser": True,
            }
        )
        if created:
            user.set_password("12345678")
            user.save()
            self.stdout.write(self.style.SUCCESS(f"[OK] Created admin user: {user.username}"))
        else:
            user.set_password("12345678")
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f"[OK] Updated admin user: {user.username}"))

        # Ensure user has proper permissions - add to Editors group
        try:
            editors_group, _ = Group.objects.get_or_create(name="Editors")
            user.groups.add(editors_group)
            self.stdout.write(self.style.SUCCESS(f"[OK] Added user to Editors group"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"[WARNING] Could not add to group: {str(e)}"))
        
        # Also ensure user has all blog permissions directly (as backup)
        try:
            from django.contrib.contenttypes.models import ContentType
            from blog.models import Post as PostModel
            
            content_type = ContentType.objects.get_for_model(PostModel)
            permissions = Permission.objects.filter(content_type=content_type)
            for perm in permissions:
                user.user_permissions.add(perm)
            self.stdout.write(self.style.SUCCESS(f"[OK] Assigned all blog permissions to user"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"[WARNING] Could not assign permissions: {str(e)}"))

        # Step 2: Ensure categories exist
        self.stdout.write("Ensuring categories exist...")
        category_names = ["Sports", "Technology", "Science", "Art", "Food"]
        categories = []
        for cat_name in category_names:
            category, _ = Category.objects.get_or_create(name=cat_name)
            categories.append(category)
        self.stdout.write(self.style.SUCCESS(f"[OK] Categories ready: {len(categories)} categories"))

        # Step 3: Create 30 posts
        self.stdout.write("Creating 30 posts...")
        
        posts_data = [
            {
                "title": "The Future of Artificial Intelligence",
                "content": "Artificial Intelligence is revolutionizing every aspect of our lives. From healthcare to transportation, AI is making processes more efficient and opening up new possibilities. Machine learning algorithms can now diagnose diseases, drive cars, and even create art. As we move forward, the integration of AI into daily life will become even more seamless.",
                "img_url": "https://picsum.photos/seed/ai1/800/600",
                "category": "Technology"
            },
            {
                "title": "Climate Change and Sustainable Solutions",
                "content": "Climate change is one of the most pressing issues of our time. Rising temperatures, melting ice caps, and extreme weather events are clear indicators of the need for immediate action. Renewable energy sources like solar and wind power offer sustainable alternatives to fossil fuels. Individual actions combined with global policies can make a significant difference.",
                "img_url": "https://picsum.photos/seed/climate1/800/600",
                "category": "Science"
            },
            {
                "title": "The Art of Modern Photography",
                "content": "Photography has evolved from a technical skill to a form of artistic expression. Modern photographers use digital tools to create stunning visual narratives. Composition, lighting, and storytelling are key elements that transform ordinary scenes into extraordinary images. The accessibility of cameras has democratized this art form.",
                "img_url": "https://picsum.photos/seed/photo1/800/600",
                "category": "Art"
            },
            {
                "title": "Exploring Quantum Computing",
                "content": "Quantum computing represents a paradigm shift in computational power. Unlike classical computers that use bits, quantum computers use quantum bits or qubits, which can exist in multiple states simultaneously. This allows quantum computers to solve complex problems that would take classical computers thousands of years in mere seconds.",
                "img_url": "https://picsum.photos/seed/quantum1/800/600",
                "category": "Technology"
            },
            {
                "title": "The Science of Nutrition",
                "content": "Understanding nutrition is essential for maintaining good health. A balanced diet provides the necessary vitamins, minerals, and macronutrients our bodies need. Recent research has shown the importance of gut health and the microbiome in overall well-being. Making informed food choices can prevent diseases and improve quality of life.",
                "img_url": "https://picsum.photos/seed/nutrition1/800/600",
                "category": "Food"
            },
            {
                "title": "Football: The Beautiful Game",
                "content": "Football, or soccer, is the world's most popular sport, bringing together billions of fans across the globe. The game combines physical fitness, strategic thinking, and teamwork. Major tournaments like the World Cup create moments of unity and celebration that transcend cultural boundaries.",
                "img_url": "https://picsum.photos/seed/football1/800/600",
                "category": "Sports"
            },
            {
                "title": "Renewable Energy Revolution",
                "content": "The shift towards renewable energy is accelerating worldwide. Solar panels and wind turbines are becoming more efficient and affordable. Energy storage solutions are improving, making renewable energy more reliable. This transition is crucial for reducing carbon emissions and combating climate change.",
                "img_url": "https://picsum.photos/seed/energy1/800/600",
                "category": "Science"
            },
            {
                "title": "Digital Art and NFTs",
                "content": "Digital art has gained mainstream recognition through NFTs and blockchain technology. Artists can now monetize their digital creations in new ways. The intersection of technology and art has created exciting opportunities for creators and collectors alike. This evolution challenges traditional notions of art ownership.",
                "img_url": "https://picsum.photos/seed/digital1/800/600",
                "category": "Art"
            },
            {
                "title": "Space Exploration Milestones",
                "content": "Humanity's journey into space continues to reach new heights. Private companies are now joining government agencies in space exploration. Missions to Mars, asteroid mining, and space tourism are becoming realities. These developments expand our understanding of the universe and our place in it.",
                "img_url": "https://picsum.photos/seed/space1/800/600",
                "category": "Science"
            },
            {
                "title": "Culinary Traditions Around the World",
                "content": "Food is a universal language that connects cultures. Each region has unique culinary traditions passed down through generations. Exploring different cuisines opens windows into diverse cultures and histories. Cooking techniques and ingredients tell stories of migration, trade, and adaptation.",
                "img_url": "https://picsum.photos/seed/culinary1/800/600",
                "category": "Food"
            },
            {
                "title": "Basketball: More Than Just a Game",
                "content": "Basketball combines athleticism, strategy, and teamwork in a fast-paced environment. The sport has produced legendary athletes who inspire millions. From street courts to professional arenas, basketball brings communities together. The game teaches valuable life lessons about perseverance and collaboration.",
                "img_url": "https://picsum.photos/seed/basketball1/800/600",
                "category": "Sports"
            },
            {
                "title": "Cybersecurity in the Digital Age",
                "content": "As our lives become more digital, cybersecurity has never been more important. Cyber threats are evolving constantly, requiring advanced defense mechanisms. Individuals and organizations must stay vigilant against phishing, malware, and data breaches. Education and awareness are key to staying safe online.",
                "img_url": "https://picsum.photos/seed/cyber1/800/600",
                "category": "Technology"
            },
            {
                "title": "The Psychology of Color in Art",
                "content": "Colors have profound psychological effects on human emotions and behavior. Artists use color theory to evoke specific feelings and create visual harmony. Different cultures associate colors with different meanings. Understanding color psychology enhances both artistic creation and appreciation.",
                "img_url": "https://picsum.photos/seed/color1/800/600",
                "category": "Art"
            },
            {
                "title": "Marine Biology Discoveries",
                "content": "The oceans hold countless mysteries waiting to be discovered. Marine biologists are uncovering new species and understanding complex ecosystems. Coral reefs, deep-sea vents, and marine life contribute to Earth's biodiversity. Protecting marine environments is crucial for the planet's health.",
                "img_url": "https://picsum.photos/seed/marine1/800/600",
                "category": "Science"
            },
            {
                "title": "Street Food Culture",
                "content": "Street food represents authentic local cuisine and cultural identity. From food trucks to night markets, street food vendors serve delicious, affordable meals. These culinary experiences offer insights into local traditions and flavors. Street food has become a global phenomenon, celebrated by food enthusiasts worldwide.",
                "img_url": "https://picsum.photos/seed/street1/800/600",
                "category": "Food"
            },
            {
                "title": "Tennis: A Game of Precision",
                "content": "Tennis requires physical endurance, mental focus, and technical skill. The sport has produced some of the greatest athletes in history. Grand Slam tournaments showcase the pinnacle of tennis excellence. The game's elegance and intensity captivate audiences worldwide.",
                "img_url": "https://picsum.photos/seed/tennis1/800/600",
                "category": "Sports"
            },
            {
                "title": "5G Technology and Connectivity",
                "content": "5G networks are transforming how we connect and communicate. With faster speeds and lower latency, 5G enables new applications like autonomous vehicles and smart cities. The technology promises to revolutionize industries from healthcare to entertainment. Widespread 5G deployment is reshaping the digital landscape.",
                "img_url": "https://picsum.photos/seed/5g1/800/600",
                "category": "Technology"
            },
            {
                "title": "Abstract Art Movements",
                "content": "Abstract art challenges viewers to interpret meaning beyond literal representation. Various movements like Cubism, Expressionism, and Minimalism have shaped modern art. Abstract artists use form, color, and composition to express emotions and ideas. This art form encourages personal interpretation and emotional connection.",
                "img_url": "https://picsum.photos/seed/abstract1/800/600",
                "category": "Art"
            },
            {
                "title": "Genetics and Personalized Medicine",
                "content": "Advances in genetics are revolutionizing healthcare through personalized medicine. Genetic testing can predict disease risk and guide treatment decisions. Gene therapy offers hope for previously untreatable conditions. Understanding our genetic makeup enables more effective and targeted medical interventions.",
                "img_url": "https://picsum.photos/seed/genetics1/800/600",
                "category": "Science"
            },
            {
                "title": "Farm-to-Table Movement",
                "content": "The farm-to-table movement emphasizes fresh, locally sourced ingredients. This approach supports local farmers and reduces environmental impact. Restaurants and consumers are increasingly valuing food transparency and sustainability. The movement promotes healthier eating and stronger community connections.",
                "img_url": "https://picsum.photos/seed/farm1/800/600",
                "category": "Food"
            },
            {
                "title": "Swimming: Building Endurance",
                "content": "Swimming is one of the most complete forms of exercise, working all major muscle groups. The sport builds cardiovascular fitness and muscular strength. Competitive swimming requires technique, discipline, and dedication. Swimming pools and open water venues offer diverse training environments.",
                "img_url": "https://picsum.photos/seed/swimming1/800/600",
                "category": "Sports"
            },
            {
                "title": "Virtual Reality Experiences",
                "content": "Virtual Reality is creating immersive experiences across entertainment, education, and training. VR technology transports users to digital worlds with unprecedented realism. Applications range from gaming to medical simulations and architectural visualization. As technology improves, VR becomes more accessible and impactful.",
                "img_url": "https://picsum.photos/seed/vr1/800/600",
                "category": "Technology"
            },
            {
                "title": "Sculpture Through the Ages",
                "content": "Sculpture has been a fundamental art form throughout human history. From ancient marble statues to modern installations, sculptures shape our understanding of form and space. Different materials and techniques reflect cultural values and technological capabilities. Contemporary sculpture continues to push creative boundaries.",
                "img_url": "https://picsum.photos/seed/sculpture1/800/600",
                "category": "Art"
            },
            {
                "title": "Climate Science Research",
                "content": "Climate scientists are working to understand and predict environmental changes. Research combines data from satellites, weather stations, and ice cores. Models help predict future climate scenarios and guide policy decisions. Scientific evidence drives global efforts to address climate challenges.",
                "img_url": "https://picsum.photos/seed/climate2/800/600",
                "category": "Science"
            },
            {
                "title": "Baking: The Science of Sweetness",
                "content": "Baking combines chemistry, precision, and creativity. Understanding how ingredients interact is key to successful baking. Temperature, timing, and technique all affect the final product. From bread to pastries, baking brings joy and satisfaction to both bakers and those who enjoy the results.",
                "img_url": "https://picsum.photos/seed/baking1/800/600",
                "category": "Food"
            },
            {
                "title": "Cricket: A Global Phenomenon",
                "content": "Cricket is one of the world's most popular sports, especially in Commonwealth nations. The game combines strategy, skill, and tradition. International tournaments like the World Cup unite fans across continents. Cricket's rich history and evolving formats keep the sport exciting and relevant.",
                "img_url": "https://picsum.photos/seed/cricket1/800/600",
                "category": "Sports"
            },
            {
                "title": "Internet of Things (IoT)",
                "content": "The Internet of Things connects everyday devices to the internet, creating smart environments. IoT devices collect and share data to automate processes and improve efficiency. Smart homes, wearable technology, and industrial sensors are examples of IoT applications. This connectivity is transforming how we live and work.",
                "img_url": "https://picsum.photos/seed/iot1/800/600",
                "category": "Technology"
            },
            {
                "title": "Watercolor Painting Techniques",
                "content": "Watercolor painting offers unique challenges and rewards. The medium's transparency and fluidity create distinctive visual effects. Artists must work quickly and plan carefully due to watercolor's unforgiving nature. Mastering techniques like wet-on-wet and glazing opens creative possibilities.",
                "img_url": "https://picsum.photos/seed/watercolor1/800/600",
                "category": "Art"
            },
            {
                "title": "Astronomy and Stargazing",
                "content": "Astronomy connects us to the vast universe beyond Earth. Observing stars, planets, and galaxies inspires wonder and scientific curiosity. Modern telescopes reveal details about distant celestial objects. Amateur astronomers contribute valuable observations to the scientific community.",
                "img_url": "https://picsum.photos/seed/astronomy1/800/600",
                "category": "Science"
            },
            {
                "title": "Coffee Culture Worldwide",
                "content": "Coffee is more than a beverage; it's a global cultural phenomenon. Different regions have unique coffee traditions and preparation methods. Coffee shops serve as social hubs and workspaces. The coffee industry supports millions of farmers and workers worldwide.",
                "img_url": "https://picsum.photos/seed/coffee1/800/600",
                "category": "Food"
            },
            {
                "title": "Olympic Games: Unity Through Sport",
                "content": "The Olympic Games bring together athletes from around the world in celebration of human achievement. The games promote peace, understanding, and excellence. Olympic athletes inspire millions with their dedication and perseverance. The event showcases the power of sport to unite diverse cultures.",
                "img_url": "https://picsum.photos/seed/olympic1/800/600",
                "category": "Sports"
            }
        ]

        created_count = 0
        with transaction.atomic():
            for post_data in posts_data:
                try:
                    # Get category
                    category = Category.objects.get(name=post_data["category"])
                    
                    # Download image from URL
                    img_url = post_data["img_url"]
                    try:
                        with urllib.request.urlopen(img_url, timeout=10) as response:
                            img_data = response.read()
                        
                        # Create a file-like object from the image data
                        img_file = BytesIO(img_data)
                        img_file.name = f"post_{created_count + 1}.jpg"
                        
                        # Create post
                        post = Post.objects.create(
                            title=post_data["title"],
                            content=post_data["content"],
                            category=category,
                            user=user,
                            is_published=True
                        )
                        
                        # Save image to the post
                        post.img_url.save(
                            img_file.name,
                            File(img_file),
                            save=True
                        )
                        
                        created_count += 1
                        self.stdout.write(f"  [OK] Created post: {post.title[:50]}...")
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f"  [WARNING] Could not download image for '{post_data['title']}': {str(e)}")
                        )
                        # Create post without image
                        Post.objects.create(
                            title=post_data["title"],
                            content=post_data["content"],
                            category=category,
                            user=user,
                            is_published=True
                        )
                        created_count += 1
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"  [ERROR] Error creating post '{post_data['title']}': {str(e)}")
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n[SUCCESS] Successfully created {created_count} posts for user '{user.username}'"
            )
        )
