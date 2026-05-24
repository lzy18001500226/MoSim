Coding Style Guidelines
#######################

C/C++
-----

This guideline is a short adaptation of the `Coding Style Guidelines <https://docs.omniverse.nvidia.com/kit/docs/carbonite/latest/CODING.html>`_
for Omniverse Carbonite SDK, the foundational software layer for Omniverse applications,microservices, tools, plugins, Connectors, and SDKs.

- Visit the Carbonite `C++17 and Beyond Recommendations <https://docs.omniverse.nvidia.com/kit/docs/carbonite/latest/CODING.html#c-17-and-beyond-recommendations>`_
  section for using C++17 features.
- Visit the Carbonite `Higher-level Concepts <https://docs.omniverse.nvidia.com/kit/docs/carbonite/latest/CODING.html#higher-level-concepts>`_
  section for using Carbonite for `thread-safety <https://docs.omniverse.nvidia.com/kit/docs/carbonite/latest/CODING.html#thread-safety>`_,
  `assertions <https://docs.omniverse.nvidia.com/kit/docs/carbonite/latest/CODING.html#assertions>`_,
  `callbacks <https://docs.omniverse.nvidia.com/kit/docs/carbonite/latest/CODING.html#callbacks>`_,
  `exceptions <https://docs.omniverse.nvidia.com/kit/docs/carbonite/latest/CODING.html#exceptions>`_,
  `logging <https://docs.omniverse.nvidia.com/kit/docs/carbonite/latest/CODING.html#logging>`_, and other topics.

Naming
^^^^^^

Prefixing and Casing
""""""""""""""""""""

The following tables outline the naming prefixing and casing used:

============== ==================
Files          Prefixing / Casing
============== ==================
namespaces     snake_case
headers (.h)   PascalCase.h
sources (.cpp) PascalCase.cpp
============== ==================

================================================= ==================
Construct                                         Prefixing / Casing
================================================= ==================
class, struct, enum class and typedef             PascalCase
constants                                         kCamelCase
enum class values                                 eCamelCase
functions                                         camelCase
private/protected functions                       _camelCase
public member variables                           camelCase
private/protected member variables                m_camelCase
private/protected static member variables         s_camelCase
global - static variable at file or project scope g_camelCase
local variables                                   camelCase
preprocessor macros                               MACRO_CASE
================================================= ==================

When a name includes an abbreviation or acronym that is commonly written entirely in uppercase,
you must still follow the casing rules laid out above. For instance:

.. code-block:: cpp

    void* gpuBuffer; // not GPUBuffer
    struct HtmlPage; // not HTMLPage
    struct UiElement; // not UIElement

Naming Guidelines
"""""""""""""""""

* All names must be written in *US English*.

* Use full English names. Don't cut the words and avoid using colloquial names.

  .. code-block:: cpp
    
      float robotVelocity; // not robotVel, or robotVelo
      struct Odometry; // not Odom

* The following names cannot be used according to the
  `C++ standard <https://en.cppreference.com/w/cpp/language/identifiers>`_:

  * Names with a double underscore anywhere are reserved (e.g.: ``__buffer``, ``object__status``).
  
  * Names that begin with an underscore followed by an uppercase letter are reserved (e.g.: ``_Buffer``).
  
  * Names that begin with an underscore are reserved in the global namespace.

* Method names must always begin with a verb (avoid confusion about what a method actually does).

  .. hint::
 
      Consult the `antonym list <https://gist.github.com/maxtruxa/b2ca551e42d3aead2b3d>`_ when naming symmetric functions.
 
  .. code-block:: cpp
 
      myVector.getLength();
      myObject.applyForce(x, y, z);
      myObject.isDynamic();
      texture.getFormat();

* The terms get/set or is/set (*bool*) should be used where an attribute is accessed directly
  (there is no significant computation overhead).

  .. code-block:: cpp

      employee.getName();
      employee.setName("Jensen Huang");
      light.isEnabled();
      light.setEnabled(true);

* Function names must indicate when a method does significant work
  (e.g.: ``computeXxxx()``, ``readXxxx()``, ``writeXxxx()``).

  .. code-block:: cpp
  
      float waveHeight = wave.computeHeight();  // NOT: wave.getHeight();

* Use stateful names for boolean variables (e.g.: ``enabled``, ``m_initialized``, ``g_cached``) and leave
  questions for methods (e.g.: ``isXxxx()`` and ``hasXxxx()``).

  .. code-block:: cpp
  
      bool isEnabled() const;
      void setEnabled(bool enabled);
      
      void doSomething()
      {
          bool initialized = m_coolSystem.isInitialized();
          ...
      }

* Avoid redundancy in naming methods (the name of the object is implicit) and functions.

  .. code-block:: cpp
  
      line.getLength();  // NOT: line.getLineLength();

* Avoid public method, arguments and member names that are likely to have been defined in the preprocessor
  (when in doubt, use another name or prefix it).

    .. code-block:: cpp
  
        size_t bufferMalloc;  // NOT: size_t malloc;
        int boundsMin, boundsMax;  // NOT: int min, max; 
        void* iface; // NOT: void* interface; (Windows.h defines `interface` as a class)

* Avoid conjunctions and sentences in names as much as possible.
  E.g.: Use ``Count`` at the end of a name for the number of items.

  .. code-block:: cpp
  
      size_t shaderCount;  // NOT: size_t numberOfShaders;
      VkBool32 skipCachedData;  // NOT: VkBool32 skipIfDataIsCached;

Coding Rules
^^^^^^^^^^^^

Files
"""""

* All files must end in blank line.

* Header files should have the extension ``.h``.

* Source files should have the extension ``.cpp`` (``.cc`` is typically used for UNIX *only* and not recommended).

* Header files must include the preprocessor directive to only include a header file once.

  .. code-block:: cpp

      #pragma once

* Source files should include the associated header in the first line of code after the commented license banner.

* Header and source files should be named with **PascalCase** and placed in their appropriate namespaced
   folder paths, which are in **lowercase**.

Include Statements
""""""""""""""""""

* Do not include ``Windows.h`` in header files as it is monolithic and pollutes the global environment for Windows.
  Instead, a much slimmer `CarbWindows.h <https://docs.omniverse.nvidia.com/kit/docs/carbonite/latest/api/file_carb_CarbWindows.h.html>`_
  exists to declare only what is needed by Carbonite. Refer to the
  `example <https://docs.omniverse.nvidia.com/kit/docs/carbonite/latest/CODING.html#include>`_ to see how to include it.

* Local includes use the path-relative include format.

* Includes of files that are not local to the code (or are pulled in via package) use the search path format.
  Isaac Sim source files (under ``plugins/`` and ``source/``) may also use search-path format
  for public headers (under ``include/``).

* If you need to associate a comment with an include put the comment on the same line as the include statement,
  otherwise clang-format will not move the chunk of code. Like this:

  .. code-block:: cpp

      #include <stdlib.h>  // this is needed for size_t on Linux

* If include order is important for some files just put ``// clang-format off``
  and ``// clang-format on`` around those lines.

Namespaces
""""""""""

* Namespaces are all lowercase.

* The C++ namespace should be project and/or team based and easily associated with the project
  (e.g.: The **Isaac Sim** project namespace is ``isaacsim::`` and is managed by the Isaac Sim team).

  .. code-block:: cpp

      namespace isaacsim
      {

* We don't add indentation for code inside namespaces (this conserves maximum space for indentation inside code).

  .. code-block:: cpp

      namespace isaacsim
      {
      namespace ros2
      {

      struct Ros2Bridge
      {

* We don't add comments for documenting closing of structs or definitions, but it's OK for namespaces because
  they often span many pages and there is no indentation to help:

  .. code-block:: cpp

      }; // end of Ros2Bridge struct    <- DON'T
      
      } // namespace ros2       <- OK
      } // namespace isaacsim   <- OK

Internal code
"""""""""""""

* For public header files, a ``details`` (internal) namespace should be used to declare implementation
  as private and subject to change, as well as signal to external users that the functions,
  types, etc. in the ``details`` namespace should not be called.

  .. code-block:: cpp

      namespace details
      {
      } // namespace details

* Within a translation unit (``.cpp`` file), use an anonymous namespace to prevent external linkage or naming
  conflicts within a module:

  .. code-block:: cpp

      namespace
      {
      } // namespace

* In general, prefer anonymous namespaces over ``static``.

Classes
"""""""

* Classes that should not be inherited from should be declared as ``final``.

* Each access modifier appears no more than once in a class, in the order: ``public``, ``protected``, ``private``.

* All ``public`` member variables live at the start of the class.

  * They have no prefix.

  * If they are accessed in a member function that access must be prefixed with ``this->``
    for improved readability and reduced head-scratching.

* All ``protected`` / ``private`` member variables live at the end of the class.

  * They are prefixed with ``m_``.

  * They should be accessed directly in member functions. Adding ``this->`` to access them is unnecessary.

* Constructors and destructor are first methods in a class after ``public`` member variables unless private scoped
  in which case they are first ``private`` methods.

* The implementations in ``.cpp`` should appears in the order which they are declared in the class.

* Avoid ``inline`` implementations unless trivial and needed for optimization.

* Use the ``override`` specifier on all overridden virtual methods. Also, every member function should have at most
  one of these specifiers: ``virtual``, ``override``, or ``final``.

* Do not override pure-virtual method with another pure-virtual method.

Structs
"""""""

* We make a clear distinction between structs and classes.

* We do not permit any member functions on structs. Those we make classes.

* If you must initialize a member of the struct then use C++14 static initializers for this, but don't do this for
  basic types like a Float3 struct because default construction/initialization is not free.

* No additional scoping is needed on struct variables.

* Not everything needs to be a class object with logic.

  * Sometimes it's better to separate the data type from the functionality and structs are a great vehicle for this.

  .. code-block:: cpp

      struct Float3
      {
          float x;
          float y;
          float z;
      };
  
      // check this out (structs are awesome):
      Float3 pointA = {0};
      Float3 pointB = {1, 0, 0};

Functions
"""""""""

* When declaring a function that accepts a pointer to a memory area and a counter or size for the area we should place
  them in a fixed order: the address first, followed by the counter. Additionally, ``size_t`` must be used as the type
  for the counter.

  .. code-block:: cpp

      void readData(const char* buffer, size_t bufferSize);
      void setNames(const char* names, size_t nameCount);
      void updateTag(const char* tag, size_t tagLength);


Enum Classes and Bit Flags
""""""""""""""""""""""""""

* We use ``enum class`` over ``enum`` to support namespaced values that do not collide.

* The values are accessed like this: ``EnumName::eSomeValue``.

* If you have an enum class as a subclass, then it should be declared inside the class directly before the constructor
  and destructor.

  .. code-block:: cpp

      class Camera
      {
      public:
  
          enum class Projection
          {
              ePerspective,
              eOrthographic
          };
  
          Camera();
  
          ~Camera();

* Note that any sequential or non-sequential enumeration is acceptable - the only rule is that the type should never
  be able to hold the value of more than one enumeration literal at any time. An example of a type that violates this
  rule is a bit mask. Those should not be represented by an enum. Instead use constant integers (``constexpr``) and group
  them by a prefix.  Also, in a ``.cpp`` file you want them to also be ``static``.  Below we show an example of a bit mask
  and bit flags:

  .. code-block:: cpp

      namespace isaacsim
      {
      namespace graphics
      {
    
      constexpr uint32_t kColorMaskRed    = 0x00000001; // static constexpr in .cpp
      constexpr uint32_t kColorMaskGreen  = 0x00000002;
      constexpr uint32_t kColorMaskBlue   = 0x00000004;
      constexpr uint32_t kColorMaskAlpha  = 0x00000008;
  
      } // namespace graphics
  
      namespace input
      {
  
      /**
       * Type used as an identifier for all subscriptions
      */
      typedef uint32_t SubscriptionId;
  
      /**
       * Defines possible press states
      */
      typedef uint32_t ButtonFlags;
      constexpr uint32_t kButtonFlagNone = 0;
      constexpr uint32_t kButtonFlagTransitionUp = 1;
      constexpr uint32_t kButtonFlagStateUp = (1 << 1);
      constexpr uint32_t kButtonFlagTransitionDown = (1 << 2);
      constexpr uint32_t kButtonFlagStateDown = (1 << 3);
  
      } // namespace input
      } // namespace isaacsim

Pre-processors and Macros
"""""""""""""""""""""""""

* It's recommended to place preprocessor definitions in the source files instead of makefiles/compiler/project files.

* Try to reduce the use of ``#define`` (e.g. for constants and small macro functions), and prefer ``constexpr`` values
  or functions when possible.

* Definitions in the public global namespace must be prefixed with the namespace in uppercase:

  .. code-block:: cpp

    #define ISAACSIM_API

* All ``#define`` macros should be set to 0, 1 or some other value.

* All checks for macros should use ``#if`` and not ``#ifdef`` or ``#if defined()``.

* When adding ``#if`` pre-processor blocks to support multiple platforms, the block must end with an ``#else`` clause
  containing the ``CARB_UNSUPPORTED_PLATFORM()`` macro. An exception to this is when the ``#else`` block
  uses entirely C++ standard code; this sometimes happens in the case of platform-specific optimizations.
  You may not make assumptions about what features future platforms may have, aside from what's in the C++ standard;
  all platform-specific code must have the associated platform specifically stated.

  .. code-block:: cpp

      #if CARB_PLATFORM_WINDOWS
          // code
      #elif CARB_PLATFORM_LINUX
          // code
      #elif CARB_PLATFORM_MACOS
          // code
      #else
          CARB_UNSUPPORTED_PLATFORM();
      #endif

  .. code-block:: cpp

      #if CARB_PLATFORM_WINDOWS
          // Windows-specific code
      #else
          // C++ standard code
      #endif

* Macros that do not have universal appeal (i.e. are only intended to be used within a single header file) shall be
  prefixed with ``ISAACSIMLOCAL_`` and ``#undef``'d at the end of the file.

Commenting and documenting
^^^^^^^^^^^^^^^^^^^^^^^^^^

License
"""""""

* The following must be included at the start (the first thing) of every header and source file:

  .. code-block:: cpp

    // SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
    // SPDX-License-Identifier: Apache-2.0
    //
    // Licensed under the Apache License, Version 2.0 (the "License");
    // you may not use this file except in compliance with the License.
    // You may obtain a copy of the License at
    //
    // http://www.apache.org/licenses/LICENSE-2.0
    //
    // Unless required by applicable law or agreed to in writing, software
    // distributed under the License is distributed on an "AS IS" BASIS,
    // WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    // See the License for the specific language governing permissions and
    // limitations under the License.

Header Files
""""""""""""

* Assume customers will read comments.

* Avoid spelling and grammatical errors.

* Header comments use *doxygen* format. We are not too sticky on *doxygen* formatting policy.

* All public **functions** and **variables** must be documented.

* The level of detail for the comment is based on the complexity for the API.

* Most important is that comments are simple and have clarity on how to use the API.

  * ``@brief`` can be dropped and automatic assumed on first line of code. Easier to read too.
  
  * ``@details`` is dropped and automatic assumed proceeding the brief line.
  
  * ``@param`` and ``@return`` are followed with a space after summary brief or details.

  .. code-block:: cpp

      /**
       * Tests whether this bounding box intersects the specified bounding box (see \ref BoundingBox class).
       *
       * You would add any specific details that may be needed here. This is
       * only necessary if there is complexity to the user of the function.
       *
       * @param box The bounding box to test intersection with.
       * @returns true if the specified bounding box intersects this bounding box, false otherwise.
       */
      bool intersects(const BoundingBox& box) const;
    
  * Overridden functions can simply refer to the base class comments.

  .. code-block:: cpp

      class Bar: public Foo
      {
      protected:

        /**
         * @see Foo::render
        */
        void render(float elapsedTime) override;

Source Files
""""""""""""

* Clean simple code is the best form of commenting.

* Do not add comments above function definitions in .cpp if they are already in header.

* Comment necessary non-obvious implementation details not the API.

* Only use ``//`` line comments on the line above the code you plan to comment.

* Avoid ``/* */``  block comments inside implementation code (.cpp). This prevents others from easily doing their own
  block comments when testing, debugging, etc.

* Avoid explicitly referring to identifiers in comments, since that's an easy way to make your comment outdated when
  an identifier is renamed.

Formatting Code
^^^^^^^^^^^^^^^

.. note::
  
    Format is enforced by `format_code.sh/format_code.bat` scripts (via `repo_format` tool)
    so there is no need to memorize them.

* We use a ``.clang-format`` file with clang-format to keep our code auto-formatted.
    
  * In some rare cases where code is manually formatted in a pleasing fashion,
    auto-formatting can be suspended with a comment block:

  .. code-block:: cpp

      // clang-format off
      ... Manually formatted code
      // clang-format on

Blocks of Code and Indentations
"""""""""""""""""""""""""""""""

* Never leave conditional code statements on same line as condition test.

  .. code-block:: cpp

      if (box.isEmpty()) return;  // DON'T

* Use braces ``{ }`` even with only one statement.

  .. code-block:: cpp

      if (box.isEmpty()) // OK
      {
          return;
      }

      for (size_t i = 0; i < count; ++i)
      {
          if (distance(sphere, points[i]) > sphere.radius)
          {
              return false;
          }
      }

Line Spacing
""""""""""""

* One line of space between function declarations in source and header.

* One line after each class scope section in header.

* Function call spacing:

  * No space before bracket or just inside brackets.

  * One space after each comma separating parameters.

  .. code-block:: cpp

      serializer->writeFloat("range", range, kLightRange);

* Conditional statement spacing:

  * One space after conditional keywords.

  * No space just inside the brackets.

  * One space separating commas, colons and condition comparison operators.

  .. code-block:: cpp

      if (enumName.compare("isaacsim::Robot::Type") == 0)
      {
          switch (static_cast<Robot::Type>(value))
          {
              case Robot::Type::eManipulator:
                  return "eManipulator";
              ...

* Don't align blocks of variables or trailing comments to match spacing causing unnecessary code changes when new
  variables are introduced:

  .. code-block:: cpp

      bool     m_very;       // Formatting  // DON'T
      float3   m_annoying;   // generates  // DON'T
      ray      m_nooNoo;     // spurious  // DON'T
      uint32_t m_dirtyBits;  // diffs.  // DON'T
